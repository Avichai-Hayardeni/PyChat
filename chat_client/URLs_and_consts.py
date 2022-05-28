IP = "localhost"
PORT = 8000

get_user_name_from_server = f"http://{IP}:{PORT}/get_user_name?user_id="

get_user_id_from_server = f"http://{IP}:{PORT}/get_user_id?user_name="

get_users_from_server = f"http://{IP}:{PORT}/get_users?users_ids="

register = f"http://{IP}:{PORT}/register"

login = f"http://{IP}:{PORT}/login"

get_all_messages = f"http://{IP}:{PORT}/get_all_messages?user_id="

get_sent_messages = f"http://{IP}:{PORT}/get_sent_messages?user_id="

get_pending_messages = f"http://{IP}:{PORT}/get_pending_messages?user_id="

send_message = f"http://{IP}:{PORT}/send_message"
