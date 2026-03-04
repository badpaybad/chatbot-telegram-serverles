import sqlite3
import uuid
import time
import json
import os

class SQLiteDB:
    def __init__(self, table_name, db_path="data/knowledgebase.db"):
        self.table_name = table_name
        self.db_path = db_path
        
        # Ensure the directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id TEXT PRIMARY KEY,
            json TEXT,
            at INTEGER
        )
        """
        with self._get_connection() as conn:
            conn.execute(query)
            conn.commit()

    def set_table_name(self, table_name):
        """
        Change the name of the active table and ensure it exists.
        """
        self.table_name = table_name
        self._create_table()

    def get_table_names(self):
        """
        Get the list of all table names in the database.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        with self._get_connection() as conn:
            cursor = conn.execute(query)
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def insert(self, data_json):
        """
        Insert a new record. data_json can be a dict or a JSON string.
        """
        record_id = str(uuid.uuid4())
        at_epoch = int(time.time())
        
        if isinstance(data_json, (dict, list)):
            data_json = json.dumps(data_json, ensure_ascii=False)
            
        query = f"INSERT INTO {self.table_name} (id, json, at) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (record_id, data_json, at_epoch))
            conn.commit()
        return record_id
    def inserts(self, data_list):
        """
        Batch insert multiple records. data_list is an array of data_json (dict or list).
        """
        at_epoch = int(time.time())
        records = []
        record_ids = []
        
        for data_json in data_list:
            record_id = str(uuid.uuid4())
            record_ids.append(record_id)
            
            if isinstance(data_json, (dict, list)):
                data_json_str = json.dumps(data_json, ensure_ascii=False)
            else:
                data_json_str = data_json
                
            records.append((record_id, data_json_str, at_epoch))
            
        query = f"INSERT INTO {self.table_name} (id, json, at) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.executemany(query, records)
            conn.commit()
            
        return record_ids


    def select(self, record_id: str | None = None, keyword: str | None = None, fromAt: int | None = None, toAt: int | None = None, limit: int | None = None):
        """
        Select records. 
        - If record_id is provided, returns that specific record (other filters ignored).
        - If keyword is provided, returns records where json content matches the keyword.
        - Support filtering by time range (fromAt, toAt) and limiting the results (limit).
        - Otherwise returns all records in the table.
        """
        result = []
        
        if record_id:
            query = f"SELECT * FROM {self.table_name} WHERE id = ?"
            with self._get_connection() as conn:
                cursor = conn.execute(query, (record_id,))
                row = cursor.fetchone()
                if row:
                    result = [{"id": row[0], "json": json.loads(row[1]), "at": row[2]}]
            return result

        # Dynamic query building for other cases
        conditions = []
        params = []

        if keyword:
            conditions.append("json LIKE ?")
            params.append(f"%{keyword}%")
        
        if fromAt is not None:
            conditions.append("at >= ?")
            params.append(fromAt)
        
        if toAt is not None:
            conditions.append("at <= ?")
            params.append(toAt)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        order_by = "ORDER BY at DESC"
        
        limit_clause = ""
        if limit is not None:
            limit_clause = f"LIMIT {int(limit)}"

        query = f"SELECT * FROM {self.table_name} {where_clause} {order_by} {limit_clause}"
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            result = [{"id": row[0], "json": json.loads(row[1]), "at": row[2]} for row in rows]
            # The user's original code had a manual result.sort(key=lambda x: x['at']) 
            # which is ASCENDING. However, the limit logic usually implies DESCENDING (top/latest).
            # The existing keyword and else blocks used ORDER BY at DESC but then sorted ASC in Python.
            # I will keep the Python sort to maintain consistent behavior with previous version.
            result.sort(key=lambda x: x['at'])

        return result

    def update(self, record_id, data_json):
        """
        Update the json content of a record by its GUID.
        """
        if isinstance(data_json, (dict, list)):
            data_json = json.dumps(data_json, ensure_ascii=False)
            
        query = f"UPDATE {self.table_name} SET json = ? WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (data_json, record_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, record_id):
        """
        Delete a record by its GUID.
        """
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.execute(query, (record_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search_json(self, field_name: str, value, fromAt: int | None = None, toAt: int | None = None, limit: int | None = None):
        """
        Search for records where a specific field in the json column matches a value.
        field_name: The name of the field (e.g., 'topic') or JSON path (e.g., '$.author.name').
        value: The value to search for.
        - Support filtering by time range (fromAt, toAt) and limiting the results (limit).
        """
        # Ensure field_name starts with $. if it's a simple key
        path = field_name if field_name.startswith("$") else f"$.{field_name}"
        result = []
        
        conditions = ["json_extract(json, ?) = ?"]
        params = [path, value]

        if fromAt is not None:
            conditions.append("at >= ?")
            params.append(fromAt)
        
        if toAt is not None:
            conditions.append("at <= ?")
            params.append(toAt)

        where_clause = "WHERE " + " AND ".join(conditions)
        order_by = "ORDER BY at DESC"
        
        limit_clause = ""
        if limit is not None:
            limit_clause = f"LIMIT {int(limit)}"

        query = f"SELECT * FROM {self.table_name} {where_clause} {order_by} {limit_clause}"
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            result = [{"id": row[0], "json": json.loads(row[1]), "at": row[2]} for row in rows]
            result.sort(key=lambda x: x['at'])
            
        return result
