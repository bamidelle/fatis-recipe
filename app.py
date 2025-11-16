import streamlit as st
import sqlite3
from datetime import datetime

# ---------------------------
#   DATABASE SETUP
# ---------------------------
conn = sqlite3.connect("fatis_recipes.db", check_same_thread=False)
c = conn.cursor()

# Table for users
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT
    )
""")

# Table for recipes
c.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        title TEXT,
        note TEXT,
        image BLOB,
        created_at TEXT
    )
""")
conn.commit()


# ---------------------------
#  LOAD OR ASK USERNAME
# ---------------------------
def get_saved_username():
    c.execute("SELECT username FROM users ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    return row[0] if row else None


username = get_saved_username()

st.title("🍳 Fati's Recipe")

if not username:
    st.header("Welcome! Let's personalize your app.")
    name_input = st.text_input("Please enter your name:")

    if st.button("Save Name"):
        if name_input.strip() == "":
            st.warning("Name cannot be empty.")
        else:
            c.execute("INSERT INTO users (username) VALUES (?)", (name_input,))
            conn.commit()
            st.success(f"Welcome, {name_input}! Your name is saved permanently.")
            st.experimental_rerun()
else:
    st.write(f"### Hello, **{username}** 👋")
    st.write("What recipe would you like to add today?")


# ---------------------------
#     ADD NEW RECIPE
# ---------------------------
if username:
    st.header("Add a New Recipe")

    recipe_title = st.text_input("Recipe Title")
    recipe_note = st.text_area("Write your recipe note:")
    uploaded_image = st.file_uploader("Upload a dish image (optional)", type=["jpg", "jpeg", "png"])

    if st.button("Save Recipe"):
        if recipe_title.strip() == "":
            st.warning("Please enter a recipe title.")
        elif recipe_note.strip() == "":
            st.warning("Please enter a recipe note.")
        else:
            image_bytes = uploaded_image.read() if uploaded_image else None

            c.execute("""
                INSERT INTO recipes (username, title, note, image, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (username, recipe_title, recipe_note, image_bytes,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

            st.success("Recipe saved successfully!")
            st.experimental_rerun()

    st.write("---")


# ---------------------------
#    VIEW USER RECIPES
# ---------------------------
if username:
    st.header("📖 Your Saved Recipes")

    c.execute("SELECT id, title, note, image, created_at FROM recipes WHERE username=? ORDER BY id DESC",
              (username,))
    rows = c.fetchall()

    if not rows:
        st.info("You haven't added any recipes yet.")
    else:
        for row in rows:
            recipe_id, title, note, image_blob, created_at = row

            st.subheader(f"🍽️ {title}")
            st.write(f"📅 *Added on:* {created_at}")
            st.write(f"📝 **Note:** {note}")

            if image_blob:
                st.image(image_blob, use_column_width=True)

            if st.button(f"Delete '{title}'", key=f"del_{recipe_id}"):
                c.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
                conn.commit()
                st.success("Recipe deleted!")
                st.experimental_rerun()

            st.write("---")
