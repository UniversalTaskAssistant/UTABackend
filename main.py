from uta.UTA import UTA

uta = UTA()
# 0. Setup user
uta.setup_user('user1', (1080, 2280), ['whatsapp', 'facebook'])

# 1. Declare task
print(uta.declare_task(user_id='user2', task_id='task1', user_msg='Send "hello" to my mom'))
print(uta.declare_task(user_id='user2', task_id='task1', user_msg='Use whatsapp'))
