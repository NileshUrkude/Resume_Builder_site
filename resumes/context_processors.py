from .utils import get_user_resume, normalize_template


def navigation(request):
    if not request.user.is_authenticated:
        return {}
    resume = get_user_resume(request)
    return {
        'active_resume': resume,
        'active_template': normalize_template(resume.preferred_template) if resume else 't1',
    }
