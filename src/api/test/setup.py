import fsutil
from node import get_node, get_dir_node, get_file_node
from user import User


root_user = User({'username': 'root'})
user1 = User({'username': 'fans656', 'groups': ['tf']})
user2 = User({'username': 'twiispa', 'groups': ['tf']})
guest_user = User({'username': ''})


fsutil.erase_everything()
root_dir = fsutil.create_root_dir()

home1 = fsutil.create_home_dir_for(user1)
home2 = fsutil.create_home_dir_for(user2)

public_dir = fsutil.create_public_dir('/public')
