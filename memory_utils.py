async def auto_save_to_memory(callback_context):
    ctx = callback_context._invocation_context
    if ctx.memory_service and ctx.session:
        await ctx.memory_service.add_session_to_memory(ctx.session)
