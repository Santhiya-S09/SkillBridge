from .models import ActivityLog
class StudentActivityMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if (
            request.user.is_authenticated
            and not request.user.is_superuser
            and request.method == 'GET'
            and response.status_code == 200
        ):
            path = request.path

            if path.startswith('/static/') or path.startswith('/media/'):
                return response

            activity_pages = {
                '/': 'Visited Home Page',
                '/dashboard/': 'Visited Dashboard',
                '/career-guidance/': 'Visited Career Guidance',
                '/skill-assessment/': 'Visited Skill Assessment',
                '/assessment-history/': 'Visited Assessment History',
                '/learning-roadmap/': 'Visited Learning Roadmap',
                '/skill-gap-analysis/': 'Visited Skill Gap Analysis',
                '/learning-center/': 'Visited Learning Center',
            }

            activity = activity_pages.get(path)

            if activity is None and '/learning-center/' in path:
                activity = 'Visited Learning Center Lesson'

            if activity:
                ActivityLog.objects.create(
                    user=request.user,
                    activity=activity
                )

        return response
