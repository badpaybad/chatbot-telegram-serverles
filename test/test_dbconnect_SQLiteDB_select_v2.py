import os
import sys
import time
import json

# Add the project root to sys.path
sys.path.append(os.getcwd())

from knowledgebase.dbconnect import SQLiteDB

def test_select_filters():
    db_path = os.path.join(os.getcwd(), "test", "test_v2_knowledgebase.db")
    db = SQLiteDB(table_name="test_filters_table", db_path=db_path)
    
    # Cleanup
    with db._get_connection() as conn:
        conn.execute(f"DROP TABLE IF EXISTS {db.table_name}")
        conn.commit()
    db._create_table()
    
    print("Inserting test records for select...")
    # Insert 5 records with specific timestamps
    # Records: t=100, t=200, t=300, t=400, t=500
    for i in range(1, 6):
        record_at = i * 100
        record_id = db.insert({"index": i, "tag": "test"})
        # Manually update 'at' because insert uses time.time()
        with db._get_connection() as conn:
            conn.execute(f"UPDATE {db.table_name} SET at = ? WHERE id = ?", (record_at, record_id))
            conn.commit()

    print("--- Test 1: select fromAt filter ---")
    results = db.select(fromAt=300)
    ats = [r['at'] for r in results]
    print(f"Results at: {ats}")
    assert set(ats) == {300, 400, 500}

    print("--- Test 2: select toAt filter ---")
    results = db.select(toAt=200)
    ats = [r['at'] for r in results]
    print(f"Results at: {ats}")
    assert set(ats) == {100, 200}

    print("--- Test 3: select fromAt and toAt filter ---")
    results = db.select(fromAt=200, toAt=400)
    ats = [r['at'] for r in results]
    print(f"Results at: {ats}")
    assert set(ats) == {200, 300, 400}

    print("--- Test 4: select limit filter (top records) ---")
    results = db.select(limit=2)
    ats = [r['at'] for r in results]
    print(f"Results at: {ats}")
    assert ats == [400, 500]

    print("--- Test 5: select keyword + limit ---")
    id6 = db.insert({"index": 6, "tag": "special"})
    id7 = db.insert({"index": 7, "tag": "special"})
    with db._get_connection() as conn:
        conn.execute(f"UPDATE {db.table_name} SET at = 1000 WHERE id = ?", (id6,))
        conn.execute(f"UPDATE {db.table_name} SET at = 1100 WHERE id = ?", (id7,))
        conn.commit()
    
    results = db.select(keyword="special", limit=1)
    print(f"Keyword limit 1 result index: {results[0]['json']['index']}")
    assert len(results) == 1
    assert results[0]['json']['index'] == 7 

    print("\n--- Testing search_json ---")
    
    print("--- Test 6: search_json fromAt ---")
    results = db.search_json("tag", "test", fromAt=400)
    ats = [r['at'] for r in results]
    print(f"Results at: {ats}")
    assert set(ats) == {400, 500}

    print("--- Test 7: search_json toAt ---")
    results = db.search_json("tag", "test", toAt=200)
    ats = [r['at'] for r in results]
    print(f"Results at: {ats}")
    assert set(ats) == {100, 200}

    print("--- Test 8: search_json limit ---")
    results = db.search_json("tag", "test", limit=2)
    ats = [r['at'] for r in results]
    print(f"Results at: {ats}")
    assert ats == [400, 500]

    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] != "config_dunp":
        print("Usage: python test/test_dbconnect_SQLiteDB_select_v2.py config_dunp")
        sys.exit(1)
    
    try:
        test_select_filters()
    except AssertionError as e:
        print(f"TEST FAILED!")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
