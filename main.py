from uta.UTA import UTA

uta = UTA()
uta.set_up_user('user2', (1080, 2280), ['whatsapp', 'facebook'])

print(uta.declare_task(user_id='user2', task_id='task1', user_msg='Send "hello" to my mom'))
print(uta.declare_task(user_id='user2', task_id='task1', user_msg='Use whatsapp'))
