#!/usr/bin/env python
"""Simple database viewer script"""
import sqlite3

def view_database(db_file="chatbot.db"):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all data
        cursor.execute("SELECT * FROM chat_history ORDER BY id")
        rows = cursor.fetchall()
        
        print("\n" + "=" * 120)
        print(f"DATABASE: {db_file} | TABLE: chat_history | TOTAL RECORDS: {len(rows)}")
        print("=" * 120)
        print(f"{'ID':<4} {'QUESTION':<50} {'ANSWER':<62}")
        print("-" * 120)
        
        for row in rows:
            id_val, question, answer = row
            q_short = (question[:48] + "...") if len(question) > 48 else question
            a_short = (answer[:60] + "...") if len(answer) > 60 else answer
            print(f"{id_val:<4} {q_short:<50} {a_short:<62}")
        
        print("-" * 120)
        print(f"✅ Total messages: {len(rows)}")
        print("=" * 120 + "\n")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_database()
