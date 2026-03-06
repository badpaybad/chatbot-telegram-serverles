
from knowledgebase.dbconnect import SQLiteDB

import knowledgebase.dbconnect as dbconnect
sqllite_all_message=dbconnect.SQLiteDB("all_message")

sqllite_all_message_file=dbconnect.SQLiteDB("all_message_file")


db_summary_chat = SQLiteDB(table_name="summary_chat")

db_jira = SQLiteDB(table_name="jira")

db_orchestration_all_message = SQLiteDB(table_name="orchestration_all_message")

db_jira_user = SQLiteDB(table_name="jira_user")

db_telegram_user = SQLiteDB(table_name="telegram_user")