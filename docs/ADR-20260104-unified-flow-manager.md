# ADR-20260104: Unified Flow Manager for Telegram Bot

## Status
Accepted

## Context
The initial Telegram bot implementation used `python-telegram-bot`'s `ConversationHandler` for managing multi-step interactions. This approach had several issues:

1. **Handler conflicts**: Multiple ConversationHandlers competed for the same messages
2. **State complexity**: Each handler had its own state machine
3. **Debugging difficulty**: Hard to understand current state across handlers
4. **Callback conflicts**: CallbackQueryHandlers often conflicted with conversation states

## Decision
Implement a **Unified Flow Manager** pattern that:

1. **Single source of truth**: All state stored in `context.user_data`
2. **Central text router**: One MessageHandler routes to flow-specific handlers
3. **Explicit state**: Clear `current_flow`, `flow_step`, `flow_data` structure
4. **Independent callbacks**: CallbackQueryHandlers work regardless of flow state

### State Structure
```python
context.user_data = {
    'current_flow': 'catalog',           # Active flow
    'flow_step': 'category_create_name', # Current step
    'flow_data': {                       # Flow-specific data
        'category_id': '...',
        'temp_name': '...',
    }
}
```

### Text Routing
```python
# text_router.py
async def route_text_input(update, context):
    step = get_flow_step(context)
    
    if step == 'category_create_name':
        return await handle_category_name(update, context)
    elif step == 'profile_edit_name':
        return await handle_profile_name(update, context)
    # ... more routes
```

### Flow Functions
```python
# flow_manager.py
def set_flow(context, flow: str, step: str, data: dict = None)
def get_flow_step(context) -> str
def clear_flow(context)
```

## Alternatives Considered
1. **Multiple ConversationHandlers**: Original approach, caused conflicts
2. **State machine library**: Overkill for this use case
3. **Redis-based state**: Network overhead, simpler in-memory sufficient

## Consequences
**Pros:**
- No handler conflicts
- Clear debugging (log `current_flow`, `flow_step`)
- Easy flow switching without ending handlers
- Callbacks work independently of text flows

**Cons:**
- Manual routing code (no automatic state transitions)
- Need to remember to clear flow when done
- Requires discipline to use flow functions consistently

## Implementation Guidelines
1. Always use `set_flow()`, `get_flow_step()`, `clear_flow()`
2. Never access `user_data` directly for flow state
3. Callback handlers should NOT modify flow state unless intentional
4. Add logging for flow transitions for debugging

## Impact on Future
- New flows can be added by defining steps and handlers
- Flow data can be persisted (to DB) for long-running processes
- Analytics can track user journeys through flows

