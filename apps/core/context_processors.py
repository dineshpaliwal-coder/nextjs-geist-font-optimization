def tenant_context(request):
    """
    Context processor to add tenant information to the context.
    Placeholder implementation.
    """
    return {
        'tenant': getattr(request, 'tenant', None)
    }
