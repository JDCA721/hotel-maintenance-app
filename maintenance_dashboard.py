# maintenance_dashboard.py

import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

DB_NAME = "hotel_maintenance.db"

# ----------------- MASTER LISTS ----------------- #

AREAS = [
    "Bathroom",
    "Bedroom",
    "Entryway",
    "Closet",
    "Kitchenette",
    "Balcony",
    "Whole Room",
    "Other",
]

FIXTURE_TYPES = [
    # Structure / surfaces
    "Walls",
    "Ceiling",
    "Trim/Baseboards",
    "Door Frame",
    "Window Frame",

    # Flooring
    "Carpet",
    "Carpet Padding",
    "Tile Floor",
    "Vinyl Floor",
    "Hardwood/Laminate Floor",

    # Doors
    "Main Entry Door",
    "Bathroom Door",
    "Closet Door",
    "Cabinet Door",
    "Patio/Balcony Door",
    "Door Lock/Deadbolt",
    "Door Handle",
    "Door Closer",
    "Door Hinges",

    # Windows & coverings
    "Window Glass",
    "Window Screen",
    "Window Lock",
    "Blinds",
    "Curtains",
    "Blackout Curtains",
    "Curtain Rod",

    # Bathroom fixtures
    "Bathroom Sink",
    "Bathroom Faucet",
    "P-Trap/Drain Under Sink",
    "Toilet",
    "Toilet Seat",
    "Toilet Flush Mechanism",
    "Shower Head",
    "Bathtub",
    "Shower Valve",
    "Tub Spout",
    "Shower/Tub Drain",
    "Exhaust Fan",
    "Vanity Mirror",
    "Towel Rack",
    "Toilet Paper Holder",
    "Bathroom Light Fixture",
    "Bathroom Vent Cover",
    "Caulking/Sealant",

    # Plumbing (general)
    "Water Supply Line",
    "Shutoff Valve",
    "Drain Line",

    # Electrical
    "Ceiling Light Fixture",
    "Lamp",
    "Outlet",
    "GFCI Outlet",
    "Light Switch",
    "USB Outlet",
    "Breaker/Power to Room",
    "Smoke Detector",
    "CO Detector",
    "Thermostat",

    # HVAC
    "HVAC Unit/Fan Coil",
    "HVAC Filter",
    "HVAC Thermostat Wiring",

    # Appliances
    "Mini Fridge",
    "Microwave",
    "Coffee Maker",
    "TV",
    "TV Remote",
    "Safe",
    "Hair Dryer",
    "Iron",
    "Ironing Board",
    "Clock/Alarm",

    # Furniture
    "Bed Frame",
    "Headboard",
    "Mattress",
    "Box Spring",
    "Nightstand",
    "Desk",
    "Desk Chair",
    "Dresser",
    "TV Stand",
    "Sofa",
    "Sofa Bed Mechanism",
    "Coffee Table",
    "Wardrobe/Armoire",

    # Balcony/Exterior
    "Balcony Railing",
    "Balcony Light Fixture",
    "Balcony Furniture",

    # Soft goods / decor
    "Rug",
    "Wall Art/Decor",

    # Safety / security
    "Door Peephole",
    "Door Latch/Chain",
    "Room Safe",

    # Catch-all
    "Other",
]

ISSUE_CATEGORIES = [
    "Leaking",
    "Clogged",
    "Slow Draining",
    "No Hot Water",
    "No Cold Water",
    "No Water",
    "Not Flushing",
    "Overflowing",
    "No Power",
    "Intermittent Power",
    "Burnt Out",
    "Flickering",
    "Won't Turn On",
    "Won't Turn Off",
    "Not Cooling",
    "Not Heating",
    "Temperature Incorrect",
    "Noisy",
    "Vibrating",
    "Loose",
    "Broken",
    "Cracked",
    "Bent",
    "Detached",
    "Stained",
    "Scuffed",
    "Scratched",
    "Peeling Paint",
    "Needs Paint",
    "Water Damage",
    "Mold/Mildew",
    "Odor Issue",
    "Missing Part",
    "Worn Out",
    "Guest Damage",
    "Installation Issue",
    "Other",
]


# ----------------- DB HELPERS ----------------- #

def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    """Create the MaintenanceTickets table if it does not exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS MaintenanceTickets (
            TicketID INTEGER PRIMARY KEY AUTOINCREMENT,
            RoomNumber TEXT NOT NULL,
            Area TEXT,
            FixtureType TEXT,
            IssueCategory TEXT,
            IssueDescription TEXT,
            Priority TEXT,
            Status TEXT,
            ReportedDateTime TEXT,
            ReportedBy TEXT,
            AssignedTo TEXT,
            StartDateTime TEXT,
            CompletedDateTime TEXT,
            Notes TEXT
        );
        """
    )

    conn.commit()
    conn.close()


def create_ticket(
    room_number: str,
    area: str,
    fixture_type: str,
    issue_category: str,
    issue_description: str,
    priority: str = "Medium",
    reported_by: str = "Staff",
    assigned_to: str = "",
):
    conn = get_connection()
    cur = conn.cursor()

    reported_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        """
        INSERT INTO MaintenanceTickets (
            RoomNumber,
            Area,
            FixtureType,
            IssueCategory,
            IssueDescription,
            Priority,
            Status,
            ReportedDateTime,
            ReportedBy,
            AssignedTo,
            StartDateTime,
            CompletedDateTime,
            Notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            room_number,
            area,
            fixture_type,
            issue_category,
            issue_description,
            priority,
            "Open",
            reported_time,
            reported_by,
            assigned_to,
            None,
            None,
            None,
        ),
    )

    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id


def get_open_tickets_df():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT TicketID, RoomNumber, Area, FixtureType, IssueCategory,
               IssueDescription, Priority, Status, ReportedDateTime,
               ReportedBy, AssignedTo
        FROM MaintenanceTickets
        WHERE Status != 'Completed'
        ORDER BY ReportedDateTime DESC;
        """,
        conn,
    )
    conn.close()
    return df


def get_all_tickets_df():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT TicketID, RoomNumber, Area, FixtureType, IssueCategory,
               IssueDescription, Priority, Status, ReportedDateTime,
               CompletedDateTime, ReportedBy, AssignedTo, Notes
        FROM MaintenanceTickets
        ORDER BY ReportedDateTime DESC;
        """,
        conn,
    )
    conn.close()
    return df


def get_room_history_df(room_number: str):
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT TicketID, RoomNumber, Area, FixtureType, IssueCategory,
               IssueDescription, Priority, Status, ReportedDateTime,
               CompletedDateTime, Notes
        FROM MaintenanceTickets
        WHERE RoomNumber = ?
        ORDER BY ReportedDateTime DESC;
        """,
        conn,
        params=(room_number,),
    )
    conn.close()
    return df


def update_ticket_status(ticket_id: int, status: str, notes: str = None, assigned_to: str = None):
    conn = get_connection()
    cur = conn.cursor()

    # Check existing start time
    cur.execute(
        "SELECT StartDateTime FROM MaintenanceTickets WHERE TicketID = ?;",
        (ticket_id,),
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        raise ValueError(f"No ticket found with ID {ticket_id}")

    start_time = row[0]
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    update_fields = ["Status = ?"]
    params = [status]

    if status == "In Progress" and not start_time:
        update_fields.append("StartDateTime = ?")
        params.append(now_str)

    if status == "Completed":
        update_fields.append("CompletedDateTime = ?")
        params.append(now_str)

    if notes is not None and notes.strip() != "":
        update_fields.append("Notes = ?")
        params.append(notes.strip())

    if assigned_to is not None and assigned_to.strip() != "":
        update_fields.append("AssignedTo = ?")
        params.append(assigned_to.strip())

    params.append(ticket_id)

    sql = f"""
        UPDATE MaintenanceTickets
        SET {", ".join(update_fields)}
        WHERE TicketID = ?;
    """

    cur.execute(sql, tuple(params))
    conn.commit()
    conn.close()


# ----------------- STREAMLIT APP ----------------- #

def main():
    st.set_page_config(page_title="Hotel Maintenance Dashboard", layout="wide")
    init_db()

    st.title("Hotel Maintenance Dashboard")

    tab_create, tab_open, tab_room, tab_update, tab_all = st.tabs(
        ["Create Ticket", "Open Tickets", "Room History", "Update Ticket", "All Tickets"]
    )

    # Tab 1: Create Ticket
    with tab_create:
        st.header("Create New Maintenance Ticket")

        with st.form("create_ticket_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                room_number = st.text_input("Room Number", placeholder="101")
                area = st.selectbox(
                    "Area",
                    AREAS,
                    index=0,
                )

            with col2:
                fixture_type = st.selectbox(
                    "Fixture / Item",
                    FIXTURE_TYPES,
                    index=0,
                )
                issue_category = st.selectbox(
                    "Issue Category",
                    ISSUE_CATEGORIES,
                    index=0,
                )

            with col3:
                priority = st.selectbox(
                    "Priority",
                    ["Low", "Medium", "High", "Emergency"],
                    index=1,
                )
                reported_by = st.selectbox(
                    "Reported By",
                    ["Guest", "Housekeeping", "Front Desk", "Manager", "Staff"],
                    index=1,
                )
                assigned_to = st.text_input("Assigned To (optional)", placeholder="Tech name")

            issue_description = st.text_area("Issue Description", height=100)

            submitted = st.form_submit_button("Create Ticket")

            if submitted:
                if not room_number or not issue_description:
                    st.error("Room number and issue description are required.")
                else:
                    ticket_id = create_ticket(
                        room_number=room_number.strip(),
                        area=area,
                        fixture_type=fixture_type,
                        issue_category=issue_category,
                        issue_description=issue_description.strip(),
                        priority=priority,
                        reported_by=reported_by,
                        assigned_to=assigned_to.strip(),
                    )
                    st.success(f"Created ticket #{ticket_id} for room {room_number.strip()}.")

    # Tab 2: Open Tickets
    with tab_open:
        st.header("Open Tickets")

        df_open = get_open_tickets_df()
        if df_open.empty:
            st.info("No open tickets.")
        else:
            st.dataframe(df_open, use_container_width=True)

            # Simple counts by fixture and priority
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Open Tickets by Fixture")
                st.bar_chart(df_open["FixtureType"].value_counts())

            with col2:
                st.subheader("Open Tickets by Priority")
                st.bar_chart(df_open["Priority"].value_counts())

    # Tab 3: Room History
    with tab_room:
        st.header("Room Maintenance History")
        room_number_search = st.text_input("Enter room number to view history", key="room_history_input")

        if st.button("Show History"):
            if not room_number_search:
                st.error("Please enter a room number.")
            else:
                df_room = get_room_history_df(room_number_search.strip())
                if df_room.empty:
                    st.info(f"No tickets found for room {room_number_search.strip()}.")
                else:
                    st.dataframe(df_room, use_container_width=True)

    # Tab 4: Update Ticket
    with tab_update:
        st.header("Update Ticket Status")

        df_open = get_open_tickets_df()
        if df_open.empty:
            st.info("No open tickets to update.")
        else:
            df_open["Label"] = df_open.apply(
                lambda row: f"#{row['TicketID']} | Room {row['RoomNumber']} | {row['FixtureType']} | {row['IssueCategory']}",
                axis=1,
            )

            selected_label = st.selectbox(
                "Select ticket to update",
                df_open["Label"].tolist(),
            )

            # Map selected label back to TicketID
            selected_ticket_id = int(selected_label.split("|")[0].strip()[1:])

            new_status = st.selectbox(
                "New Status",
                ["Open", "In Progress", "Completed"],
                index=1,
            )
            new_assigned_to = st.text_input("Assigned To (optional, update)")
            new_notes = st.text_area("Notes (optional)", height=100)

            if st.button("Update Ticket"):
                try:
                    update_ticket_status(
                        ticket_id=selected_ticket_id,
                        status=new_status,
                        notes=new_notes,
                        assigned_to=new_assigned_to,
                    )
                    st.success(f"Updated ticket #{selected_ticket_id} to status '{new_status}'.")
                except ValueError as e:
                    st.error(str(e))

    # Tab 5: All Tickets
    with tab_all:
        st.header("All Tickets")
        df_all = get_all_tickets_df()
        if df_all.empty:
            st.info("No tickets in the system yet.")
        else:
            st.dataframe(df_all, use_container_width=True)


if __name__ == "__main__":
    main()
