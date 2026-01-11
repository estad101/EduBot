import sys
sys.path.insert(0, '.')
from services.conversation_service import MessageRouter, ConversationState

buttons = MessageRouter.get_buttons(
    intent='faq',
    current_state=ConversationState.IDLE,
    is_registered=True
)

print('FAQ Buttons:')
for btn in buttons:
    print(f'  {btn["title"]}')
