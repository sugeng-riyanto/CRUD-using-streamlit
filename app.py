import streamlit as st
import sqlite3
from datetime import datetime
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records
                 (id INTEGER PRIMARY KEY, text TEXT, number INTEGER, date TEXT, image BLOB, signature BLOB)''')
    conn.commit()
    conn.close()

# Insert Record
def insert_record(text, number, date, image, signature):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO records (text, number, date, image, signature) VALUES (?, ?, ?, ?, ?)",
              (text, number, date, image, signature))
    conn.commit()
    conn.close()

# Update Record
def update_record(record_id, text, number, date, image, signature):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE records SET text = ?, number = ?, date = ?, image = ?, signature = ? WHERE id = ?",
              (text, number, date, image, signature, record_id))
    conn.commit()
    conn.close()

# Delete Record
def delete_record(record_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

# Fetch Record by ID
def fetch_record_by_id(record_id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM records WHERE id = ?", (record_id,))
    record = c.fetchone()
    conn.close()
    return record

# Fetch All Records
def fetch_records():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM records")
    records = c.fetchall()
    conn.close()
    return records

# Convert Image to Binary
def convert_image_to_binary(img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# Convert Binary to Image
def convert_binary_to_image(binary):
    img_byte_arr = io.BytesIO(binary)
    img = Image.open(img_byte_arr)
    return img

# Streamlit Application
def main():
    st.title("CRUD Application with Streamlit and SQLite")

    menu = ["Create", "Read", "Update", "Delete"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Initialize the Database
    init_db()

    if choice == "Create":
        st.subheader("Create Record")

        with st.form(key='create_form'):
            text = st.text_input("Enter text")
            number = st.number_input("Enter number", step=1)
            date = st.date_input("Enter date", datetime.now())
            image = st.file_uploader("Upload image", type=['png', 'jpg', 'jpeg'])
            st.write("Draw your signature below:")
            signature_canvas = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",  # Fill color with some opacity
                stroke_width=2,
                stroke_color="#000",
                background_color="#fff",
                update_streamlit=True,
                height=150,
                width=400,
                drawing_mode="freedraw",
                key="signature_canvas_create",
            )
            submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                if image is not None:
                    image = Image.open(image)
                    image = convert_image_to_binary(image)

                signature = None
                if signature_canvas.image_data is not None:
                    signature = Image.fromarray(signature_canvas.image_data.astype('uint8'), 'RGBA')
                    signature = convert_image_to_binary(signature)

                insert_record(text, number, date, image, signature)
                st.success("Record created successfully")

    elif choice == "Read":
        st.subheader("Read Records")
        records = fetch_records()
        for record in records:
            st.write(f"ID: {record[0]}")
            st.write(f"Text: {record[1]}")
            st.write(f"Number: {record[2]}")
            st.write(f"Date: {record[3]}")
            if record[4]:
                st.image(convert_binary_to_image(record[4]), caption="Image", use_column_width=True)
            if record[5]:
                st.image(convert_binary_to_image(record[5]), caption="Signature", use_column_width=True)

    elif choice == "Update":
        st.subheader("Update Record")
        if "show_update_form" not in st.session_state:
            st.session_state.show_update_form = False
        
        record_id = st.number_input("Enter Record ID to Update", step=1)
        if st.button("Fetch Record"):
            record = fetch_record_by_id(record_id)
            if record:
                st.session_state.show_update_form = True
                st.session_state.record = record
            else:
                st.error("Record not found")

        if st.session_state.show_update_form:
            record = st.session_state.record
            with st.form(key='update_form'):
                text = st.text_input("Update text", record[1])
                number = st.number_input("Update number", value=record[2], step=1)
                date = st.date_input("Update date", datetime.strptime(record[3], "%Y-%m-%d"))

                image = st.file_uploader("Upload new image", type=['png', 'jpg', 'jpeg'])
                st.write("Draw your new signature below:")
                signature_canvas = st_canvas(
                    fill_color="rgba(255, 165, 0, 0.3)",  # Fill color with some opacity
                    stroke_width=2,
                    stroke_color="#000",
                    background_color="#fff",
                    update_streamlit=True,
                    height=150,
                    width=400,
                    drawing_mode="freedraw",
                    key="signature_canvas_update",
                )

                submit_button = st.form_submit_button(label='Update')

                if submit_button:
                    if image is not None:
                        image = Image.open(image)
                        image = convert_image_to_binary(image)

                    signature = None
                    if signature_canvas.image_data is not None:
                        signature = Image.fromarray(signature_canvas.image_data.astype('uint8'), 'RGBA')
                        signature = convert_image_to_binary(signature)

                    update_record(record_id, text, number, date, image, signature)
                    st.success("Record updated successfully")
                    st.session_state.show_update_form = False

    elif choice == "Delete":
        st.subheader("Delete Record")
        record_id = st.number_input("Enter Record ID to Delete", step=1)
        if st.button("Delete Record"):
            delete_record(record_id)
            st.success("Record deleted successfully")

if __name__ == '__main__':
    main()
