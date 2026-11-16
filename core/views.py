
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    RoadmapProgress,
    SkillAssessment,
    LessonProgress,
    ActivityLog,
    StudentProfile
)

def home(request):
    return render(request, 'core/home.html')


def logout(request):
    auth_logout(request)
    return redirect('home')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'core/dashboard.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')

        if not name or not email or not phone_number or not password:
            messages.error(request, 'Please fill all fields.')

        elif not phone_number.isdigit() or len(phone_number) != 10:
            messages.error(request, 'Enter a valid 10-digit phone number.')

        elif User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered.')

        elif StudentProfile.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered.')

        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )

            StudentProfile.objects.create(
                user=user,
                phone_number=phone_number
            )

            messages.success(
                request,
                'Registration successful! Please login.'
            )
            return redirect('login')

    return render(request, 'core/register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')

        if not email or not phone_number or not password:
            messages.error(request, 'Please fill all fields.')

        elif not phone_number.isdigit() or len(phone_number) != 10:
            messages.error(request, 'Enter a valid 10-digit phone number.')

        else:
            user = authenticate(
                request,
                username=email,
                password=password
            )

            if user is None or user.is_superuser or user.is_staff:
                messages.error(
                    request,
                    'Invalid email, phone number or password.'
                )

            else:
                profile, created = StudentProfile.objects.get_or_create(
                    user=user
                )

                if not profile.phone_number:
                    phone_exists = StudentProfile.objects.filter(
                        phone_number=phone_number
                    ).exclude(user=user).exists()

                    if phone_exists:
                        messages.error(
                            request,
                            'This phone number is already registered.'
                        )
                    else:
                        profile.phone_number = phone_number
                        profile.save()
                        auth_login(request, user)
                        return redirect('dashboard')

                elif profile.phone_number == phone_number:
                    auth_login(request, user)
                    return redirect('dashboard')

                else:
                    messages.error(
                        request,
                        'Phone number does not match.'
                    )

    return render(request, 'core/login.html')

@login_required(login_url='login')
def career_guidance(request):
    if request.method == 'POST':
        interests = request.POST.get('interests', '').strip()
        skills = request.POST.get('skills', '').strip()
        education = request.POST.get('education', '').strip()
        goal = request.POST.get('goal', '').strip()

        career_roadmaps = {
            'Python Developer': [
                'Learn Python fundamentals, variables and data types.',
                'Practice functions, OOP and exception handling.',
                'Learn Django framework and database integration.',
                'Build a complete Python Django web application.',
                'Learn Git, prepare your portfolio and practice interviews.'
            ],
            'Web Developer': [
                'Learn HTML and CSS fundamentals.',
                'Practice JavaScript and DOM manipulation.',
                'Learn responsive web design using Bootstrap.',
                'Learn Django backend development and databases.',
                'Build and deploy a complete full-stack website.'
            ],
            'Data Analyst': [
                'Learn Python fundamentals and basic statistics.',
                'Practice SQL queries and database concepts.',
                'Learn Pandas and NumPy for data handling.',
                'Create charts using data visualization tools.',
                'Build data analysis projects for your portfolio.'
            ],
            'AI Engineer': [
                'Strengthen Python programming fundamentals.',
                'Learn mathematics and statistics basics.',
                'Practice data handling using Python libraries.',
                'Understand machine learning fundamentals.',
                'Build beginner-friendly AI projects.'
            ],
            'Not Sure': [
                'Explore different IT career paths and job roles.',
                'Learn basic Python programming.',
                'Practice HTML, CSS and SQL fundamentals.',
                'Try small projects in different IT domains.',
                'Choose a career path based on your interests and practice.'
            ]
        }

        suggestions = career_roadmaps.get(
            goal,
            career_roadmaps['Not Sure']
        )

        if goal in career_roadmaps:
            ActivityLog.objects.create(
                user=request.user,
                activity=f'Selected Career Goal: {goal}'
            )

        return render(
            request,
            'core/career-guidance.html',
            {
                'interests': interests,
                'skills': skills,
                'education': education,
                'goal': goal,
                'suggestions': suggestions,
                'error_message': '',
            }
        )

    return render(request, 'core/career-guidance.html')
# SKILL ASSESSMENT


@login_required(login_url='login')
def skill_assessment(request):
    skill_fields = {
        'Python': 'python_skill',
        'Django': 'django_skill',
        'SQL': 'sql_skill',
        'HTML': 'html_skill',
        'CSS': 'css_skill',
        'JavaScript': 'javascript_skill',
    }

    if request.method == 'POST':
        scores = {}

        try:
            for skill, field in skill_fields.items():
                score = int(request.POST.get(field, '0'))

                if not 1 <= score <= 5:
                    raise ValueError

                scores[skill] = score

        except (TypeError, ValueError):
            messages.error(
                request,
                'Please select a valid rating for every skill.'
            )
            return render(request, 'core/skill_assessment.html')

        average = sum(scores.values()) / len(scores)

        if average >= 4:
            level = 'Advanced'
        elif average >= 3:
            level = 'Intermediate'
        else:
            level = 'Beginner'

        SkillAssessment.objects.create(
            user=request.user,
            scores=scores,
            average_score=average,
            level=level
        )

        # SAVE STUDENT ACTIVITY
        ActivityLog.objects.create(
            user=request.user,
            activity='Submitted Skill Assessment'
        )

        messages.success(
            request,
            'Your skill assessment result has been saved successfully!'
        )

        return render(
            request,
            'core/skill_assessment.html',
            {
                'scores': scores,
                'average': average,
                'level': level,
            }
        )

    return render(request, 'core/skill_assessment.html')


@login_required(login_url='login')
def assessment_history(request):
    assessments = SkillAssessment.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'core/assessment-history.html',
        {'assessments': assessments}
    )


# LEARNING ROADMAP


@login_required(login_url='login')
def learning_roadmap(request):
    roadmaps = {
        'Python Developer': [
            'Python fundamentals and functions',
            'OOP, modules and exception handling',
            'Django and database integration',
            'Build a complete Django project',
            'Git, portfolio and interview preparation'
        ],
        'Web Developer': [
            'HTML and CSS fundamentals',
            'JavaScript basics and DOM',
            'Responsive design with Bootstrap',
            'Django backend and database',
            'Build and deploy a full-stack website'
        ],
        'Data Analyst': [
            'Python fundamentals',
            'SQL and database queries',
            'Pandas data analysis',
            'Charts and data visualization',
            'Build a data analysis portfolio project'
        ],
        'AI Engineer': [
            'Python fundamentals',
            'Math and statistics basics',
            'Data handling with Python',
            'Machine learning fundamentals',
            'Build beginner AI projects'
        ]
    }

    goal = ''
    steps = []
    completed_steps = []
    completed_lessons = []
    completed_lesson_count = 0
    generated = False

    if request.method == 'POST':
        goal = request.POST.get('goal', '').strip()
        action = request.POST.get('action', '')

        if goal not in roadmaps:
            messages.error(
                request,
                'Please select a valid career goal.'
            )
            goal = ''

        elif action in ['generate_roadmap', 'generate']:
            generated = True

        elif action == 'save_progress':
            generated = True

    elif request.method == 'GET':
        selected_goal = request.GET.get('goal', '').strip()

        if selected_goal in roadmaps:
            goal = selected_goal
            generated = True

    if generated and goal in roadmaps:
        steps = roadmaps[goal]

        progress, created = RoadmapProgress.objects.get_or_create(
            user=request.user,
            career_goal=goal,
            defaults={'completed_steps': []}
        )

        if (
            request.method == 'POST'
            and request.POST.get('action') == 'save_progress'
        ):
            selected_steps = request.POST.getlist('completed_steps')

            new_completed_steps = [
                step for step in selected_steps
                if step in steps
            ]

            old_completed_steps = progress.completed_steps or []

            if set(new_completed_steps) != set(old_completed_steps):

                progress.completed_steps = new_completed_steps
                progress.save()

                ActivityLog.objects.create(
                    user=request.user,
                    activity=f'Updated Roadmap Progress: {goal}'
                )

        completed_steps = progress.completed_steps or []

        completed_lessons = list(
            LessonProgress.objects.filter(
                user=request.user,
                career_goal=goal,
                is_completed=True
            ).values_list('lesson_number', flat=True)
        )

        completed_lesson_count = len(completed_lessons)

    return render(
        request,
        'core/learning-roadmap.html',
        {
            'roadmaps': roadmaps,
            'goal': goal,
            'steps': steps,
            'generated': generated,
            'completed_steps': completed_steps,
            'completed_lessons': completed_lessons,
            'completed_lesson_count': completed_lesson_count,
        }
    )

# FREE RULE-BASED SKILL GAP ANALYSIS

@login_required(login_url='login')
def skill_gap_analysis(request):

    assessment = SkillAssessment.objects.filter(
        user=request.user
    ).order_by('-created_at').first()

    analysis = ''
    error_message = ''

    if assessment is None:
        error_message = (
            'Please complete your Skill Assessment first '
            'to get your Skill Gap Analysis.'
        )

    else:
        scores = assessment.scores

        strong_skills = []
        improving_skills = []
        moderate_skills = []

        for skill, score in scores.items():
            score = float(score)

            if score >= 4:
                strong_skills.append((skill, score))
            elif score <= 3:
                improving_skills.append((skill, score))
            else:
                moderate_skills.append((skill, score))

        recommendations = {
            'Python': 'Practice Python fundamentals, functions, OOP and small coding programs.',
            'Django': 'Learn Django views, URL routing, models, forms and database integration.',
            'SQL': 'Practice SELECT, WHERE, JOIN, GROUP BY and aggregate functions.',
            'HTML': 'Practice semantic HTML, forms, tables and webpage structure.',
            'CSS': 'Improve CSS layouts, Flexbox, Grid, responsive design and styling.',
            'JavaScript': 'Practice variables, functions, DOM manipulation and event handling.',
        }

        result = []

        result.append('SKILL GAP ANALYSIS REPORT')
        result.append('=' * 35)

        result.append(f'\nOverall Level: {assessment.level}')
        result.append(
            f'Average Score: {assessment.average_score:.2f} / 5'
        )

        result.append('\n1. STRONG SKILLS')

        if strong_skills:
            for skill, score in strong_skills:
                result.append(f'- {skill}: {score:.1f}/5')
        else:
            result.append(
                '- No strong skills identified yet. Keep practicing!'
            )

        result.append('\n2. SKILLS TO IMPROVE')

        if improving_skills:
            for skill, score in improving_skills:
                result.append(f'- {skill}: {score:.1f}/5')
        else:
            result.append('- No major skill gaps identified.')

        result.append('\n3. SKILLS TO DEVELOP FURTHER')

        if moderate_skills:
            for skill, score in moderate_skills:
                result.append(f'- {skill}: {score:.1f}/5')
        else:
            result.append('- Keep maintaining your current skills.')

        result.append('\n4. PERSONALIZED IMPROVEMENT SUGGESTIONS')

        skills_to_develop = improving_skills + moderate_skills

        if skills_to_develop:
            for skill, score in skills_to_develop:
                suggestion = recommendations.get(
                    skill,
                    'Practice regularly and complete practical exercises.'
                )
                result.append(f'- {skill}: {suggestion}')
        else:
            result.append(
                '- Continue learning advanced concepts and building projects.'
            )

        result.append('\n5. YOUR 5-STEP LEARNING PLAN')

        learning_steps = [
            'Revise your basic programming concepts and understand your current skill gaps.',
            'Practice the skills with the lowest assessment scores first.',
            'Complete small practical exercises for Python, SQL and web development.',
            'Build a mini project that combines your technical skills.',
            'Review your progress and take another Skill Assessment.'
        ]

        priority_skills = sorted(
            scores.items(),
            key=lambda item: float(item[1])
        )

        for index, (skill, score) in enumerate(priority_skills[:3]):
            suggestion = recommendations.get(
                skill,
                'Practice this skill with practical exercises.'
            )
            learning_steps[index] = f'Improve {skill}: {suggestion}'

        for index, step in enumerate(learning_steps, start=1):
            result.append(f'{index}. {step}')

        result.append(
            '\nNote: This report is based on your self-assessment ratings. '
            'Your actual skill level can be improved through practice and projects.'
        )

        analysis = '\n'.join(result)

    return render(
        request,
        'core/skill-gap-analysis.html',
        {
            'assessment': assessment,
            'analysis': analysis,
            'error_message': error_message,
        }
    )


# EXISTING PYTHON DEVELOPER LESSONS
# These five working lessons are kept unchanged.



@login_required(login_url='login')
def learning_center(request, step_number):

    lessons = {
        1: 'core/learning-center.html',
        2: 'core/learning-center-2.html',
        3: 'core/learning-center-3.html',
        4: 'core/learning-center-4.html',
        5: 'core/learning-center-5.html',
    }

    roadmap_steps = {
        1: 'Python fundamentals and functions',
        2: 'OOP, modules and exception handling',
        3: 'Django and database integration',
        4: 'Build a complete Django project',
        5: 'Git, portfolio and interview preparation',
    }

    if step_number not in lessons:
        return redirect('learning_roadmap')

    career_goal = 'Python Developer'

    if request.method == 'POST':

        if request.POST.get('action') == 'complete_lesson':

            lesson, created = LessonProgress.objects.update_or_create(
                user=request.user,
                career_goal=career_goal,
                lesson_number=step_number,
                defaults={
                    'is_completed': True,
                    'completed_at': timezone.now(),
                }
            )

            # SAVE STUDENT ACTIVITY ONLY ON FIRST COMPLETION
            if created:
                ActivityLog.objects.create(
                    user=request.user,
                    activity=f'Completed Lesson {step_number}: {roadmap_steps[step_number]}'
                )

            messages.success(
                request,
                'Lesson completed successfully!'
            )

            return redirect(
                'learning_center',
                step_number=step_number
            )

    lesson_progress = LessonProgress.objects.filter(
        user=request.user,
        career_goal=career_goal,
        lesson_number=step_number,
        is_completed=True
    ).first()

    if lesson_progress:

        roadmap_progress, created = RoadmapProgress.objects.get_or_create(
            user=request.user,
            career_goal=career_goal,
            defaults={'completed_steps': []}
        )

        completed_steps = roadmap_progress.completed_steps
        current_step = roadmap_steps[step_number]

        if current_step not in completed_steps:
            completed_steps.append(current_step)
            roadmap_progress.completed_steps = completed_steps
            roadmap_progress.save()

    return render(
        request,
        lessons[step_number],
        {
            'step_number': step_number,
            'career_goal': career_goal,
            'is_completed': lesson_progress is not None,
        }
    )

# LESSON CONTENT HELPER

def create_lesson(title, objective, topics, sections,
                  practice, exercises, quiz):

    return {
        'title': title,
        'objective': objective,
        'topics': topics,
        'sections': sections,
        'practice': practice,
        'exercises': exercises,
        'quiz': quiz,
    }


# NEW WEB DEVELOPER, DATA ANALYST AND AI ENGINEER LESSONS

CAREER_LESSONS = {

    # WEB DEVELOPER

    'web-developer': {
        'career': 'Web Developer',

        'steps': [
            'HTML and CSS fundamentals',
            'JavaScript basics and DOM',
            'Responsive design with Bootstrap',
            'Django backend and database',
            'Build and deploy a full-stack website'
        ],

        'lessons': {

            1: create_lesson(
                'HTML and CSS Fundamentals',
                'Learn to create structured webpages and style them using CSS.',
                [
                    'HTML document structure',
                    'Headings, paragraphs, links and images',
                    'HTML forms and input elements',
                    'CSS selectors and properties',
                    'Colors, fonts, margins and padding'
                ],
                [
                    {
                        'title': 'Introduction to HTML',
                        'explanation': 'HTML stands for HyperText Markup Language. It is used to create the structure of webpages. HTML uses tags to organize content such as headings, paragraphs, images and links. A browser reads HTML and displays the webpage.',
                        'tamil': 'HTML na webpage-oda basic structure create panna use panra language.',
                        'example': '''<!DOCTYPE html>
<html>
<head>
    <title>My First Page</title>
</head>
<body>
    <h1>Welcome to My Website</h1>
    <p>This is my first webpage.</p>
</body>
</html>''',
                        'output': 'Welcome to My Website\nThis is my first webpage.',
                        'note': 'The head contains page information. The body contains visible webpage content.'
                    },
                    {
                        'title': 'HTML Elements and Attributes',
                        'explanation': 'HTML elements are created using tags. The h1 tag displays a heading, p displays a paragraph and a creates a hyperlink. Attributes provide additional information. For example, href specifies the destination of a link.',
                        'tamil': 'Tags use panni content display pannuvom. Attributes use panni extra information kuduppom.',
                        'example': '''<h1>My Profile</h1>
<p>I am learning web development.</p>
<a href="https://example.com">Visit Website</a>''',
                        'output': 'A heading, a paragraph and a clickable Visit Website link.',
                        'note': 'Most HTML elements have opening and closing tags.'
                    },
                    {
                        'title': 'Introduction to CSS',
                        'explanation': 'CSS stands for Cascading Style Sheets. It controls how HTML elements look. CSS can change text colors, background colors, font sizes, spacing and borders. It helps make a webpage attractive and readable.',
                        'tamil': 'HTML structure create pannum. CSS andha structure-ku color and design kudukkum.',
                        'example': '''h1 {
    color: purple;
    font-size: 30px;
}

p {
    color: gray;
    background-color: #f5eaff;
}''',
                        'output': 'The heading appears purple and larger. The paragraph appears gray with a light purple background.',
                        'note': 'A CSS rule contains a selector and declarations.'
                    }
                ],
                'Create a personal profile webpage using HTML and CSS.',
                [
                    'Create a webpage with your name as the main heading.',
                    'Add an About Me paragraph and an image.',
                    'Add a hyperlink to another website.',
                    'Use CSS to change the background and heading colors.'
                ],
                [
                    {
                        'question': 'What is the full form of HTML?',
                        'options': ['HyperText Markup Language', 'HighText Machine Language', 'Hyper Transfer Main Language', 'Home Tool Markup Language'],
                        'answer': 'HyperText Markup Language'
                    },
                    {
                        'question': 'Which tag creates the largest standard heading?',
                        'options': ['<h6>', '<heading>', '<h1>', '<head>'],
                        'answer': '<h1>'
                    },
                    {
                        'question': 'Which HTML tag creates a hyperlink?',
                        'options': ['<link>', '<a>', '<href>', '<url>'],
                        'answer': '<a>'
                    },
                    {
                        'question': 'What does CSS control?',
                        'options': ['Database records', 'Webpage appearance and styling', 'Server hardware', 'Internet connection'],
                        'answer': 'Webpage appearance and styling'
                    },
                    {
                        'question': 'Which CSS property changes text color?',
                        'options': ['font-size', 'background', 'color', 'margin'],
                        'answer': 'color'
                    }
                ]
            ),

            2: create_lesson(
                'JavaScript Basics and DOM',
                'Learn JavaScript programming and make webpages interactive.',
                [
                    'JavaScript introduction',
                    'Variables and data types',
                    'Conditions and loops',
                    'Functions and events',
                    'DOM selection and manipulation'
                ],
                [
                    {
                        'title': 'Introduction to JavaScript',
                        'explanation': 'JavaScript is a programming language used to add interactive behavior to webpages. HTML creates structure, CSS controls appearance and JavaScript controls actions. Examples include button clicks, form validation and changing webpage content.',
                        'tamil': 'Button click pannumbodhu action nadakkanum na JavaScript use pannuvom.',
                        'example': '''<button onclick="alert('Welcome!')">
    Click Me
</button>''',
                        'output': 'When the user clicks the button, a Welcome! alert appears.',
                        'note': 'JavaScript can be written inside a script tag or in a separate .js file.'
                    },
                    {
                        'title': 'Variables and Data Types',
                        'explanation': 'Variables store information that a program can use later. JavaScript provides let and const for declaring variables. Common data types include strings, numbers, booleans, arrays and objects. Use let when a value may change and const when it should not be reassigned.',
                        'tamil': 'Variable na data store panna use panra container maadhiri.',
                        'example': '''let studentName = "Anu";
let age = 21;
const course = "Web Development";

console.log(studentName);
console.log(age);
console.log(course);''',
                        'output': 'Anu\n21\nWeb Development',
                        'note': 'Use meaningful variable names to make code easier to understand.'
                    },
                    {
                        'title': 'Conditions, Loops and DOM',
                        'explanation': 'Conditions help a program make decisions. Loops repeat code. The DOM represents a webpage as objects that JavaScript can access and change. Events such as button clicks can trigger JavaScript functions.',
                        'tamil': 'Condition use panni decision edukka mudiyum. DOM use panni webpage content change pannalaam.',
                        'example': '''<p id="message">Original Message</p>
<button onclick="changeMessage()">Change</button>

<script>
function changeMessage() {
    document.getElementById("message").textContent =
        "Message Changed!";
}
</script>''',
                        'output': 'Before click: Original Message\nAfter click: Message Changed!',
                        'note': 'getElementById selects an element using its ID.'
                    }
                ],
                'Create a webpage button that changes a message when clicked.',
                [
                    'Create variables for name, age and course.',
                    'Write an if-else program to check whether a mark is a pass.',
                    'Use a for loop to display numbers from 1 to 5.',
                    'Create a button that changes a paragraph using the DOM.'
                ],
                [
                    {
                        'question': 'Which language adds interactivity to webpages?',
                        'options': ['HTML', 'CSS', 'JavaScript', 'SQL'],
                        'answer': 'JavaScript'
                    },
                    {
                        'question': 'Which keyword declares a variable that can be reassigned?',
                        'options': ['const', 'let', 'fixed', 'static'],
                        'answer': 'let'
                    },
                    {
                        'question': 'Which statement is used for decision-making?',
                        'options': ['if', 'print', 'import', 'style'],
                        'answer': 'if'
                    },
                    {
                        'question': 'Which method selects an element by its ID?',
                        'options': ['getElementById()', 'getElementByClass()', 'selectId()', 'findElement()'],
                        'answer': 'getElementById()'
                    },
                    {
                        'question': 'What is a function?',
                        'options': ['A reusable block of code', 'A CSS color', 'An HTML image', 'A database table'],
                        'answer': 'A reusable block of code'
                    }
                ]
            ),

            3: create_lesson(
                'Responsive Design with Bootstrap',
                'Create webpages that adapt to mobile, tablet and desktop screens.',
                [
                    'Responsive web design',
                    'Bootstrap introduction',
                    'Containers and grid system',
                    'Bootstrap cards and buttons',
                    'Responsive navigation bars'
                ],
                [
                    {
                        'title': 'Responsive Web Design',
                        'explanation': 'Responsive web design means creating a webpage that adjusts to different screen sizes. Flexible layouts, responsive images and CSS media queries help content fit different devices.',
                        'tamil': 'Oru website mobile, tablet, laptop ellathulayum correct-ah display aaganum. Adhu dhaan responsive design.',
                        'example': '''.container {
    width: 90%;
    margin: auto;
}

@media (max-width: 600px) {
    .container {
        width: 100%;
    }
}''',
                        'output': 'The container uses 90% width normally and 100% width on screens up to 600px.',
                        'note': 'The viewport meta tag helps mobile browsers use the device width.'
                    },
                    {
                        'title': 'Introduction to Bootstrap',
                        'explanation': 'Bootstrap is a frontend CSS framework that provides ready-made styles and components. It helps developers create responsive websites faster. Bootstrap includes buttons, cards, forms and navigation bars.',
                        'tamil': 'Bootstrap-la ready-made design classes irukkum. Adha use panna styling easy-ah mudiyum.',
                        'example': '''<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

<button class="btn btn-primary">
    Get Started
</button>''',
                        'output': 'A styled blue Bootstrap button appears.',
                        'note': 'Include the Bootstrap stylesheet before using its CSS classes.'
                    },
                    {
                        'title': 'Bootstrap Grid and Components',
                        'explanation': 'Bootstrap uses a 12-column grid system. A container holds rows, and each row contains columns. Components such as cards and buttons help create consistent page layouts.',
                        'tamil': 'Grid system use panni content-a rows and columns-ah arrange pannalaam.',
                        'example': '''<div class="container">
    <div class="row">
        <div class="col-md-6">First Column</div>
        <div class="col-md-6">Second Column</div>
    </div>
</div>''',
                        'output': 'Two equal-width columns appear side by side on medium and larger screens.',
                        'note': 'On smaller screens, these columns stack vertically.'
                    }
                ],
                'Create a responsive webpage with a navbar and three information cards.',
                [
                    'Add the Bootstrap 5 stylesheet to a webpage.',
                    'Create a container with two columns.',
                    'Create three cards with different titles.',
                    'Build a simple responsive navigation bar.'
                ],
                [
                    {
                        'question': 'What is responsive web design?',
                        'options': ['A website that adapts to screen sizes', 'A database design', 'A programming language', 'A server configuration'],
                        'answer': 'A website that adapts to screen sizes'
                    },
                    {
                        'question': 'What is Bootstrap?',
                        'options': ['A database', 'A frontend CSS framework', 'A programming language', 'An operating system'],
                        'answer': 'A frontend CSS framework'
                    },
                    {
                        'question': 'How many columns are in the Bootstrap grid?',
                        'options': ['6', '8', '10', '12'],
                        'answer': '12'
                    },
                    {
                        'question': 'Which class creates a Bootstrap primary button?',
                        'options': ['btn-primary', 'button-blue', 'primary-button', 'blue-btn'],
                        'answer': 'btn-primary'
                    },
                    {
                        'question': 'Which Bootstrap component displays grouped information?',
                        'options': ['Card', 'Loop', 'Database', 'Variable'],
                        'answer': 'Card'
                    }
                ]
            ),

            4: create_lesson(
                'Django Backend and Database',
                'Understand how Django handles requests and stores website information.',
                [
                    'Django project and app structure',
                    'URL routing and views',
                    'Django templates',
                    'Models and migrations',
                    'Displaying database records'
                ],
                [
                    {
                        'title': 'Introduction to Django',
                        'explanation': 'Django is a Python web framework used to build web applications. It provides tools for URL routing, views, templates, database operations and user authentication. Django follows the Model-Template-View architecture.',
                        'tamil': 'Django na Python use panni backend website build panna help panra framework.',
                        'example': '''python -m django startproject myproject
cd myproject
python manage.py startapp students''',
                        'output': 'A Django project named myproject and an app named students are created.',
                        'note': 'A project contains overall configuration. An app contains a specific set of features.'
                    },
                    {
                        'title': 'URLs and Views',
                        'explanation': 'A URL pattern connects a browser address to a Django view. A view is a Python function or class that receives a request and returns a response. Views can process forms and render templates.',
                        'tamil': 'User URL open pannumbodhu endha Python function run aaganum nu URL routing decide pannum.',
                        'example': '''# views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Django")

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]''',
                        'output': 'Opening the configured home URL displays: Welcome to Django',
                        'note': 'The URL pattern maps the home route to the home view.'
                    },
                    {
                        'title': 'Templates, Models and Migrations',
                        'explanation': 'Templates display dynamic HTML content. Django models define database record structures using Python classes. Migrations translate model changes into database schema changes.',
                        'tamil': 'Template page display panna, Model database structure define panna, Migration database changes apply panna use aagum.',
                        'example': '''# models.py
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

# Terminal
python manage.py makemigrations
python manage.py migrate''',
                        'output': 'Django creates and applies a migration for the Student model.',
                        'note': 'makemigrations creates migration files. migrate applies those changes to the database.'
                    }
                ],
                'Create a Django app that saves and displays student details.',
                [
                    'Create a Django app named students.',
                    'Create a home view that returns a response.',
                    'Connect a URL pattern to the view.',
                    'Create a Student model with name and email fields.',
                    'Create and apply migrations.'
                ],
                [
                    {
                        'question': 'Django is written in which programming language?',
                        'options': ['Java', 'Python', 'C++', 'JavaScript'],
                        'answer': 'Python'
                    },
                    {
                        'question': 'Which file commonly contains Django application views?',
                        'options': ['views.py', 'style.css', 'index.js', 'manage.html'],
                        'answer': 'views.py'
                    },
                    {
                        'question': 'Which function renders a template?',
                        'options': ['render()', 'print()', 'input()', 'connect()'],
                        'answer': 'render()'
                    },
                    {
                        'question': 'What does a Django model define?',
                        'options': ['Database structure', 'Page colors', 'Browser settings', 'CSS animations'],
                        'answer': 'Database structure'
                    },
                    {
                        'question': 'Which command applies migrations?',
                        'options': ['python manage.py migrate', 'python manage.py runserver', 'python manage.py startapp', 'python manage.py check'],
                        'answer': 'python manage.py migrate'
                    }
                ]
            ),

            5: create_lesson(
                'Build and Deploy a Full-Stack Website',
                'Combine frontend, backend and database skills to create a complete web application.',
                [
                    'Project planning and requirements',
                    'Frontend and backend integration',
                    'Database operations',
                    'Testing and debugging',
                    'Deployment fundamentals'
                ],
                [
                    {
                        'title': 'Planning a Web Project',
                        'explanation': 'Before writing code, identify the purpose of the website and its users. List required pages, features and data. Create a simple layout plan and divide the project into smaller tasks.',
                        'tamil': 'Coding start panna munnaadi website purpose, users, pages and features decide pannanum.',
                        'example': '''Student Information Website

Pages:
1. Home
2. Register
3. Login
4. Student Dashboard

Features:
- User registration
- Login authentication
- Student profile
- Database storage''',
                        'output': 'A project plan with four pages and four main features.',
                        'note': 'A clear project plan makes development more organized.'
                    },
                    {
                        'title': 'Connecting Frontend and Backend',
                        'explanation': 'The frontend is the part users interact with, such as forms and buttons. The backend processes requests and performs application logic. In Django, HTML forms send data to views, and views process that data before returning a response.',
                        'tamil': 'Frontend user-kitta data collect pannum. Backend andha data process panni response kudukkum.',
                        'example': '''# views.py
from django.shortcuts import render

def welcome(request):
    name = request.GET.get('name', 'Student')
    return render(request, 'welcome.html', {
        'name': name
    })

# welcome.html
<h2>Hello {{ name }}</h2>''',
                        'output': 'Opening the page with ?name=Anu displays Hello Anu.',
                        'note': 'GET reads query parameters from the URL. Avoid sending sensitive information through query parameters.'
                    },
                    {
                        'title': 'Database Integration and Testing',
                        'explanation': 'A database stores application information so it can be retrieved later. Django ORM allows developers to create, read, update and delete records using Python. Testing helps identify errors before a website is released.',
                        'tamil': 'Database-la project data store pannuvom. Testing use panni features correct-ah work aagudha nu check pannuvom.',
                        'example': '''# Create a record
Student.objects.create(
    name="Anu",
    email="anu@example.com"
)

# Retrieve records
students = Student.objects.all()

# Check project
python manage.py check
python manage.py test''',
                        'output': 'A student record is created, records can be retrieved, and Django project checks can be run.',
                        'note': 'The Student model and its database migration must already exist.'
                    }
                ],
                'Build a simple student information website using Django and a database.',
                [
                    'Write down the requirements for a student website.',
                    'Create Home, Register and Login pages.',
                    'Connect a form to a Django view.',
                    'Store student information using a Django model.',
                    'Test the application and document its features.'
                ],
                [
                    {
                        'question': 'What is the first step in a web project?',
                        'options': ['Project planning', 'Deleting the database', 'Deployment', 'Buying a server'],
                        'answer': 'Project planning'
                    },
                    {
                        'question': 'Which part handles application logic?',
                        'options': ['Frontend', 'Backend', 'Browser theme', 'CSS'],
                        'answer': 'Backend'
                    },
                    {
                        'question': 'What is the purpose of a database?',
                        'options': ['Store and retrieve information', 'Change font colors', 'Create animations', 'Resize images'],
                        'answer': 'Store and retrieve information'
                    },
                    {
                        'question': 'Why is testing important?',
                        'options': ['To find errors and verify features', 'To change the project name', 'To remove all users', 'To avoid writing code'],
                        'answer': 'To find errors and verify features'
                    },
                    {
                        'question': 'What does deployment mean?',
                        'options': ['Making an application available on a server', 'Writing a CSS selector', 'Creating a variable', 'Deleting a project'],
                        'answer': 'Making an application available on a server'
                    }
                ]
            )
        }
    },


    # DATA ANALYST

    'data-analyst': {
        'career': 'Data Analyst',

        'steps': [
            'Python fundamentals',
            'SQL and database queries',
            'Pandas data analysis',
            'Charts and data visualization',
            'Build a data analysis portfolio project'
        ],

        'lessons': {

            1: create_lesson(
                'Python Fundamentals for Data Analysis',
                'Learn Python basics used when working with data.',
                [
                    'Variables and data types',
                    'Lists, tuples and dictionaries',
                    'Conditions and loops',
                    'Functions',
                    'Working with simple data'
                ],
                [
                    {
                        'title': 'Variables and Data Types',
                        'explanation': 'Variables store values that can be used in a program. Python supports data types such as integers, floats, strings and booleans. Data analysts use variables to store values, labels and calculated results.',
                        'tamil': 'Variable na data store panna use panra container maadhiri.',
                        'example': '''student_name = "Anu"
mark = 85
average = 82.5
is_passed = True

print(student_name)
print(mark)
print(average)
print(is_passed)''',
                        'output': 'Anu\n85\n82.5\nTrue',
                        'note': 'Python identifies the data type automatically from the assigned value.'
                    },
                    {
                        'title': 'Lists and Dictionaries',
                        'explanation': 'A list stores multiple values in an ordered collection. A dictionary stores information as key-value pairs. These structures are useful for organizing marks, names and other datasets.',
                        'tamil': 'List-la multiple values store pannalaam. Dictionary-la key and value format-la data store pannalaam.',
                        'example': '''marks = [80, 90, 75, 85]

student = {
    "name": "Anu",
    "mark": 85
}

print(marks[0])
print(student["name"])''',
                        'output': '80\nAnu',
                        'note': 'List indexing starts at zero. Dictionary values can be accessed using their keys.'
                    },
                    {
                        'title': 'Conditions, Loops and Functions',
                        'explanation': 'Conditions help a program make decisions based on data. Loops process multiple values. Functions group reusable operations, such as calculating an average or checking a result.',
                        'tamil': 'Data-la irukkura values-a process panna conditions and loops use pannuvom. Repeated work-ku functions use pannuvom.',
                        'example': '''marks = [80, 90, 70]

def calculate_average(values):
    return sum(values) / len(values)

average = calculate_average(marks)

if average >= 50:
    print("Pass")

print(average)''',
                        'output': 'Pass\n80.0',
                        'note': 'The function receives a list and returns its average.'
                    }
                ],
                'Write a Python program to calculate the average of five marks.',
                [
                    'Create variables for a student name and mark.',
                    'Create a list containing five marks.',
                    'Find the highest mark using max().',
                    'Write a function to calculate the average.',
                    'Use an if-else statement to display Pass or Fail.'
                ],
                [
                    {
                        'question': 'Which data type stores whole numbers?',
                        'options': ['int', 'str', 'bool', 'list'],
                        'answer': 'int'
                    },
                    {
                        'question': 'Which Python structure stores multiple ordered values?',
                        'options': ['List', 'Integer', 'Boolean', 'Float'],
                        'answer': 'List'
                    },
                    {
                        'question': 'Which function calculates the total of numeric values?',
                        'options': ['sum()', 'print()', 'input()', 'type()'],
                        'answer': 'sum()'
                    },
                    {
                        'question': 'Which keyword defines a function?',
                        'options': ['def', 'class', 'for', 'if'],
                        'answer': 'def'
                    },
                    {
                        'question': 'Which operator checks equality?',
                        'options': ['=', '==', '!=', '>='],
                        'answer': '=='
                    }
                ]
            ),

            2: create_lesson(
                'SQL and Database Queries',
                'Learn how to retrieve and manage information in a database.',
                [
                    'Database and table concepts',
                    'SELECT and WHERE statements',
                    'ORDER BY and DISTINCT',
                    'INSERT, UPDATE and DELETE',
                    'COUNT, SUM, AVG and GROUP BY'
                ],
                [
                    {
                        'title': 'Introduction to Databases and SQL',
                        'explanation': 'A database stores organized information. Data is commonly arranged in tables containing rows and columns. SQL stands for Structured Query Language. It is used to communicate with relational databases.',
                        'tamil': 'Database-la data tables format-la store aagum. SQL use panni andha data retrieve and manage pannuvom.',
                        'example': '''CREATE TABLE Students (
    id INT,
    name VARCHAR(100),
    mark INT
);''',
                        'output': 'A Students table is created with id, name and mark columns.',
                        'note': 'SQL syntax may have small differences between database systems.'
                    },
                    {
                        'title': 'Retrieving and Filtering Data',
                        'explanation': 'SELECT retrieves information from a table. WHERE filters records based on a condition. ORDER BY sorts the result. DISTINCT removes duplicate values from the selected result.',
                        'tamil': 'SELECT data edukkum. WHERE condition use panni required records mattum filter pannum.',
                        'example': '''SELECT * FROM Students;

SELECT name, mark
FROM Students
WHERE mark >= 50;

SELECT * FROM Students
ORDER BY mark DESC;''',
                        'output': 'The first query displays all records. The second displays students with marks of 50 or more. The third sorts students by mark in descending order.',
                        'note': 'DESC sorts from highest to lowest; ASC sorts from lowest to highest.'
                    },
                    {
                        'title': 'SQL Functions and Data Changes',
                        'explanation': 'Aggregate functions calculate summaries from multiple rows. COUNT counts records, SUM adds values and AVG calculates an average. INSERT adds records, UPDATE changes records and DELETE removes records.',
                        'tamil': 'SQL aggregate functions use panni total, count, average maadhiri summary calculate pannalaam.',
                        'example': '''SELECT COUNT(*) FROM Students;

SELECT AVG(mark) FROM Students;

INSERT INTO Students (id, name, mark)
VALUES (1, 'Anu', 85);''',
                        'output': 'The queries count students, calculate average marks and insert a student record.',
                        'note': 'Use a suitable WHERE condition with UPDATE and DELETE when only selected records should be changed.'
                    }
                ],
                'Create a student table and write queries to filter and count records.',
                [
                    'Create a Students table with id, name and mark.',
                    'Insert three student records.',
                    'Display all students using SELECT.',
                    'Filter students who scored above 70.',
                    'Calculate the average mark using AVG().'
                ],
                [
                    {
                        'question': 'What is the full form of SQL?',
                        'options': ['Structured Query Language', 'Simple Question Language', 'System Query List', 'Standard Quick Language'],
                        'answer': 'Structured Query Language'
                    },
                    {
                        'question': 'Which command retrieves records?',
                        'options': ['SELECT', 'DELETE', 'DROP', 'UPDATE'],
                        'answer': 'SELECT'
                    },
                    {
                        'question': 'Which clause filters records?',
                        'options': ['WHERE', 'ORDER BY', 'CREATE', 'INSERT'],
                        'answer': 'WHERE'
                    },
                    {
                        'question': 'Which function calculates an average?',
                        'options': ['AVG()', 'COUNT()', 'SUM()', 'MAX()'],
                        'answer': 'AVG()'
                    },
                    {
                        'question': 'Which command adds a new record?',
                        'options': ['INSERT', 'SELECT', 'UPDATE', 'DROP'],
                        'answer': 'INSERT'
                    }
                ]
            ),

            3: create_lesson(
                'Pandas Data Analysis',
                'Understand how Python can organize and analyze datasets.',
                [
                    'Introduction to Pandas',
                    'Series and DataFrames',
                    'Loading CSV files',
                    'Selecting and filtering rows',
                    'Handling missing values'
                ],
                [
                    {
                        'title': 'Introduction to Pandas',
                        'explanation': 'Pandas is a Python library used for data manipulation and analysis. It provides tools to load, organize, filter and summarize datasets. It is commonly used when working with spreadsheet-like data.',
                        'tamil': 'Pandas na Python library. Table format data easy-ah read and analyze panna use aagum.',
                        'example': '''import pandas as pd

data = {
    "Name": ["Anu", "Ravi", "Kavi"],
    "Mark": [85, 70, 90]
}

df = pd.DataFrame(data)
print(df)''',
                        'output': 'A table with Name and Mark columns is displayed.',
                        'note': 'Install Pandas in your Python environment before running the example.'
                    },
                    {
                        'title': 'Series and DataFrames',
                        'explanation': 'A Series is a one-dimensional labeled collection of values. A DataFrame is a two-dimensional table with rows and columns. DataFrames are especially useful for working with structured datasets.',
                        'tamil': 'Series single column maadhiri. DataFrame multiple rows and columns irukkura table maadhiri.',
                        'example': '''import pandas as pd

marks = pd.Series([80, 90, 75])
print(marks)

students = pd.DataFrame({
    "Name": ["Anu", "Ravi"],
    "Mark": [80, 90]
})
print(students)''',
                        'output': 'The first output is a Series. The second output is a DataFrame with two columns.',
                        'note': 'A DataFrame can contain multiple Series as its columns.'
                    },
                    {
                        'title': 'Reading and Filtering CSV Data',
                        'explanation': 'CSV stands for Comma-Separated Values. It stores tabular information in a text file. Pandas can read CSV files into DataFrames. You can select columns, filter rows and check missing values.',
                        'tamil': 'CSV file-la irukkura table data-va Pandas use panni Python-la analyze pannalaam.',
                        'example': '''import pandas as pd

df = pd.read_csv("students.csv")

print(df.head())
print(df["Name"])
print(df[df["Mark"] >= 80])
print(df.isnull().sum())''',
                        'output': 'The first rows, Name column, students with marks of 80 or more, and missing-value counts are displayed.',
                        'note': 'The students.csv file must be available at the specified path.'
                    }
                ],
                'Load a CSV file and calculate the average of a numeric column.',
                [
                    'Import the Pandas library.',
                    'Create a DataFrame using a dictionary.',
                    'Display the first five rows using head().',
                    'Filter records based on a numeric column.',
                    'Check missing values using isnull().sum().'
                ],
                [
                    {
                        'question': 'What is Pandas?',
                        'options': ['A Python data analysis library', 'A database server', 'A web browser', 'A programming language'],
                        'answer': 'A Python data analysis library'
                    },
                    {
                        'question': 'Which function creates a DataFrame?',
                        'options': ['pd.DataFrame()', 'pd.Table()', 'pd.Rows()', 'pd.Create()'],
                        'answer': 'pd.DataFrame()'
                    },
                    {
                        'question': 'Which function reads a CSV file?',
                        'options': ['read_csv()', 'read_html()', 'open_table()', 'load_data()'],
                        'answer': 'read_csv()'
                    },
                    {
                        'question': 'Which method displays the first rows?',
                        'options': ['head()', 'tail_only()', 'first()', 'show()'],
                        'answer': 'head()'
                    },
                    {
                        'question': 'Which method checks missing values?',
                        'options': ['isnull()', 'isfull()', 'emptycheck()', 'missing()'],
                        'answer': 'isnull()'
                    }
                ]
            ),

            4: create_lesson(
                'Charts and Data Visualization',
                'Learn how to present data in a clear visual format.',
                [
                    'Why data visualization is useful',
                    'Bar charts and line charts',
                    'Pie charts',
                    'Choosing a suitable chart',
                    'Adding chart titles and labels'
                ],
                [
                    {
                        'title': 'Introduction to Data Visualization',
                        'explanation': 'Data visualization represents information using charts and graphs. It helps people understand patterns, differences and trends more easily than reading a large table of numbers.',
                        'tamil': 'Numbers mattum paakradha vida chart-la paatha comparison and patterns easy-ah puriyum.',
                        'example': '''import matplotlib.pyplot as plt

subjects = ["Python", "SQL", "HTML"]
marks = [85, 75, 90]

plt.bar(subjects, marks)
plt.title("Subject Marks")
plt.xlabel("Subjects")
plt.ylabel("Marks")
plt.show()''',
                        'output': 'A bar chart displays marks for Python, SQL and HTML.',
                        'note': 'Matplotlib is a Python library used to create charts.'
                    },
                    {
                        'title': 'Common Chart Types',
                        'explanation': 'A bar chart compares categories. A line chart shows changes over time. A pie chart represents proportions of a whole. Choosing the correct chart makes the information easier to understand.',
                        'tamil': 'Bar chart comparison-ku, line chart time trend-ku, pie chart percentage share-ku useful.',
                        'example': '''import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar"]
sales = [100, 150, 130]

plt.plot(months, sales)
plt.title("Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.show()''',
                        'output': 'A line chart displays monthly sales values.',
                        'note': 'Use a chart type that matches the question you want to answer.'
                    },
                    {
                        'title': 'Interpreting Charts',
                        'explanation': 'After creating a chart, read its title, axes, labels and values. Compare categories and look for patterns. A chart should represent the original data accurately and should not hide important information.',
                        'tamil': 'Chart create pannina mattum podhadhu. Adhula enna information irukku nu explain panna theriyanum.',
                        'example': '''subjects = ["Python", "SQL", "HTML"]
marks = [85, 75, 90]

highest = max(marks)
print("Highest mark:", highest)''',
                        'output': 'Highest mark: 90',
                        'note': 'The HTML category has the highest value in this example.'
                    }
                ],
                'Create a chart showing the marks of five students.',
                [
                    'Create a list of five student names.',
                    'Create a list of their marks.',
                    'Draw a bar chart using Matplotlib.',
                    'Add a title and axis labels.',
                    'Write two observations about the chart.'
                ],
                [
                    {
                        'question': 'What is data visualization?',
                        'options': ['Representing data visually', 'Deleting data', 'Creating passwords', 'Writing HTML only'],
                        'answer': 'Representing data visually'
                    },
                    {
                        'question': 'Which chart is suitable for comparing categories?',
                        'options': ['Bar chart', 'Line chart', 'Network map', 'Text file'],
                        'answer': 'Bar chart'
                    },
                    {
                        'question': 'Which chart commonly shows trends over time?',
                        'options': ['Line chart', 'Pie chart', 'Table only', 'Icon'],
                        'answer': 'Line chart'
                    },
                    {
                        'question': 'Which Python library can create charts?',
                        'options': ['Matplotlib', 'Django', 'Requests', 'Flask'],
                        'answer': 'Matplotlib'
                    },
                    {
                        'question': 'Why are chart labels useful?',
                        'options': ['They explain what values represent', 'They delete values', 'They change the database', 'They hide the data'],
                        'answer': 'They explain what values represent'
                    }
                ]
            ),

            5: create_lesson(
                'Build a Data Analysis Portfolio Project',
                'Apply data analysis concepts in a beginner project.',
                [
                    'Choose a simple dataset',
                    'Understand columns and data types',
                    'Clean and organize the dataset',
                    'Calculate useful summaries',
                    'Create charts and explain findings'
                ],
                [
                    {
                        'title': 'Choose and Understand a Dataset',
                        'explanation': 'A dataset is a collection of related information. Before analysis, understand what each row and column represents. Check the column names, data types and number of records. Choose a small dataset with a clear purpose.',
                        'tamil': 'Dataset analyze panna munnaadi adhu enna data, each column enna meaning nu understand pannanum.',
                        'example': '''import pandas as pd

df = pd.DataFrame({
    "Student": ["Anu", "Ravi", "Kavi"],
    "Mark": [85, 70, 90]
})

print(df.shape)
print(df.columns)
print(df.dtypes)''',
                        'output': 'The program displays the dataset dimensions, column names and data types.',
                        'note': 'Understanding the dataset is the first step in meaningful analysis.'
                    },
                    {
                        'title': 'Clean and Summarize Data',
                        'explanation': 'Data cleaning improves data quality. It includes checking missing values, removing unwanted duplicates and correcting inconsistent values. Summary statistics help describe the dataset using count, average, minimum and maximum values.',
                        'tamil': 'Wrong or missing values irundha analysis result affect aagum. Adhanala data clean pannanum.',
                        'example': '''print(df.isnull().sum())

df = df.drop_duplicates()

print(df["Mark"].mean())
print(df["Mark"].max())
print(df["Mark"].min())''',
                        'output': 'The program displays missing-value counts, removes duplicate rows and calculates mark summaries.',
                        'note': 'Choose a suitable approach before removing missing data from a real dataset.'
                    },
                    {
                        'title': 'Present Findings',
                        'explanation': 'A good data analysis project should explain the question, dataset, cleaning process, calculations and findings. Charts can make results easier to understand. The final report should clearly explain what the data shows and any limitations.',
                        'tamil': 'Project mudichadhum result enna, enna learn pannom nu simple-ah report-la explain pannanum.',
                        'example': '''average_mark = df["Mark"].mean()
highest_mark = df["Mark"].max()

print("Average:", average_mark)
print("Highest:", highest_mark)''',
                        'output': 'The program displays the average and highest marks from the dataset.',
                        'note': 'Do not make conclusions that are not supported by the available data.'
                    }
                ],
                'Analyze a student marks dataset and prepare a short findings report.',
                [
                    'Select or create a small student marks dataset.',
                    'Display the number of rows and columns.',
                    'Check missing and duplicate records.',
                    'Calculate average, minimum and maximum marks.',
                    'Create one chart and write three findings.'
                ],
                [
                    {
                        'question': 'What is a dataset?',
                        'options': ['A collection of related data', 'A CSS file', 'A web browser', 'A programming language'],
                        'answer': 'A collection of related data'
                    },
                    {
                        'question': 'Why is data cleaning important?',
                        'options': ['To improve data quality', 'To change the computer', 'To create a website', 'To delete every column'],
                        'answer': 'To improve data quality'
                    },
                    {
                        'question': 'Which method removes duplicate rows in Pandas?',
                        'options': ['drop_duplicates()', 'remove_all()', 'delete_table()', 'clear_rows()'],
                        'answer': 'drop_duplicates()'
                    },
                    {
                        'question': 'Which function finds the maximum value?',
                        'options': ['max()', 'min()', 'mean()', 'count()'],
                        'answer': 'max()'
                    },
                    {
                        'question': 'What should a project report explain?',
                        'options': ['Methods and findings', 'Only the project name', 'Only computer details', 'Unrelated information'],
                        'answer': 'Methods and findings'
                    }
                ]
            )
        }
    },


    # AI ENGINEER

    'ai-engineer': {
        'career': 'AI Engineer',

        'steps': [
            'Python fundamentals',
            'Math and statistics basics',
            'Data handling with Python',
            'Machine learning fundamentals',
            'Build beginner AI projects'
        ],

        'lessons': {

            1: create_lesson(
                'Python Fundamentals for AI',
                'Build the programming foundation needed for AI learning.',
                [
                    'Variables and data types',
                    'Lists and dictionaries',
                    'Conditions and loops',
                    'Functions',
                    'Basic problem-solving with Python'
                ],
                [
                    {
                        'title': 'Python Variables and Data Types',
                        'explanation': 'Python is a programming language widely used in AI development. Variables store information, while data types describe the kind of information stored. Common types include integers, floats, strings and booleans.',
                        'tamil': 'AI learn panna Python basics strong-ah therinjirukkanum. Variables data store panna help pannum.',
                        'example': '''model_name = "Beginner AI Model"
accuracy = 0.92
number_of_records = 100
is_trained = True

print(model_name)
print(accuracy)
print(number_of_records)
print(is_trained)''',
                        'output': 'Beginner AI Model\n0.92\n100\nTrue',
                        'note': 'These are example values used to understand Python variables.'
                    },
                    {
                        'title': 'Lists and Dictionaries',
                        'explanation': 'Lists store multiple values in order. Dictionaries store information using key-value pairs. These structures help organize data before it is processed by an AI program.',
                        'tamil': 'Multiple data values organize panna list and dictionary use pannuvom.',
                        'example': '''marks = [80, 85, 90]

student = {
    "name": "Anu",
    "mark": 85
}

print(marks)
print(student["name"])''',
                        'output': '[80, 85, 90]\nAnu',
                        'note': 'Lists use numeric indexes, while dictionaries use keys.'
                    },
                    {
                        'title': 'Conditions, Loops and Functions',
                        'explanation': 'Conditions allow programs to make decisions. Loops repeat operations, and functions group reusable instructions. These concepts are important when preparing and processing information for AI applications.',
                        'tamil': 'AI program-la repeated data process panna loops and reusable operations-ku functions use pannuvom.',
                        'example': '''numbers = [10, 20, 30]

def calculate_total(values):
    total = 0
    for number in values:
        total += number
    return total

print(calculate_total(numbers))''',
                        'output': '60',
                        'note': 'The function receives a list and returns the sum of its values.'
                    }
                ],
                'Write a Python program that finds the largest number in a list.',
                [
                    'Create variables for a name and age.',
                    'Create a list containing five numbers.',
                    'Find the largest value using max().',
                    'Write a function to calculate a total.',
                    'Use a loop to display every value in a list.'
                ],
                [
                    {
                        'question': 'Which language is widely used in AI development?',
                        'options': ['Python', 'HTML', 'CSS', 'XML'],
                        'answer': 'Python'
                    },
                    {
                        'question': 'Which data type stores decimal numbers?',
                        'options': ['float', 'int', 'str', 'bool'],
                        'answer': 'float'
                    },
                    {
                        'question': 'Which structure stores key-value pairs?',
                        'options': ['Dictionary', 'String', 'Integer', 'Boolean'],
                        'answer': 'Dictionary'
                    },
                    {
                        'question': 'Which keyword defines a Python function?',
                        'options': ['def', 'for', 'if', 'return'],
                        'answer': 'def'
                    },
                    {
                        'question': 'Which function returns the largest value?',
                        'options': ['max()', 'min()', 'sum()', 'len()'],
                        'answer': 'max()'
                    }
                ]
            ),

            2: create_lesson(
                'Math and Statistics Basics',
                'Understand basic mathematical ideas used in data and AI.',
                [
                    'Numbers and basic arithmetic',
                    'Mean, median and mode',
                    'Percentages and ratios',
                    'Introduction to probability',
                    'Understanding simple data patterns'
                ],
                [
                    {
                        'title': 'Mean, Median and Mode',
                        'explanation': 'Statistics helps us understand and summarize data. Mean is the average of values. Median is the middle value after sorting. Mode is the value that occurs most often. These measures describe different aspects of a dataset.',
                        'tamil': 'Mean average. Median middle value. Mode repeated-ah varra value.',
                        'example': '''import statistics

marks = [60, 70, 70, 80, 90]

print(statistics.mean(marks))
print(statistics.median(marks))
print(statistics.mode(marks))''',
                        'output': 'Mean: 74\nMedian: 70\nMode: 70',
                        'note': 'Statistics functions can help summarize numeric datasets.'
                    },
                    {
                        'title': 'Percentages and Ratios',
                        'explanation': 'A percentage expresses a value as a part of 100. A ratio compares two quantities. These concepts are useful for understanding proportions and comparing values in datasets.',
                        'tamil': 'Percentage na 100-la evlo nu sollum. Ratio rendu values compare panna use aagum.',
                        'example': '''scored_marks = 80
total_marks = 100

percentage = (scored_marks / total_marks) * 100

print(percentage)''',
                        'output': '80.0',
                        'note': 'The percentage formula is obtained by dividing the obtained value by the total and multiplying by 100.'
                    },
                    {
                        'title': 'Introduction to Probability',
                        'explanation': 'Probability measures how likely an event is to happen. Its value ranges from 0 to 1. A value of 0 means impossible, while 1 means certain. Probability helps describe uncertainty in data and AI.',
                        'tamil': 'Oru event nadakka chance evlo irukku nu probability explain pannum.',
                        'example': '''favorable_outcomes = 1
total_outcomes = 2

probability = favorable_outcomes / total_outcomes

print(probability)''',
                        'output': '0.5',
                        'note': 'This example represents one favorable outcome out of two equally likely outcomes.'
                    }
                ],
                'Calculate the mean, median and mode of a small set of numbers.',
                [
                    'Calculate the average of five numbers.',
                    'Find the median after sorting a list.',
                    'Find the most frequent value in a list.',
                    'Calculate a percentage using Python.',
                    'Write a simple probability example.'
                ],
                [
                    {
                        'question': 'What is the mean?',
                        'options': ['Average of values', 'Middle value only', 'Most frequent value', 'Largest value'],
                        'answer': 'Average of values'
                    },
                    {
                        'question': 'What is the median?',
                        'options': ['Middle value after sorting', 'Total of values', 'Smallest value', 'Percentage'],
                        'answer': 'Middle value after sorting'
                    },
                    {
                        'question': 'What is the mode?',
                        'options': ['Most frequent value', 'Average', 'Middle value', 'Total'],
                        'answer': 'Most frequent value'
                    },
                    {
                        'question': 'What is the usual range of probability?',
                        'options': ['0 to 1', '1 to 10', '10 to 100', '-10 to -1'],
                        'answer': '0 to 1'
                    },
                    {
                        'question': 'How is a percentage calculated?',
                        'options': ['Part divided by total multiplied by 100', 'Part plus total', 'Total minus part', 'Part multiplied by total'],
                        'answer': 'Part divided by total multiplied by 100'
                    }
                ]
            ),

            3: create_lesson(
                'Data Handling with Python',
                'Learn how to prepare data before using machine learning.',
                [
                    'Introduction to NumPy arrays',
                    'Introduction to Pandas DataFrames',
                    'Reading CSV datasets',
                    'Checking missing values',
                    'Filtering and organizing data'
                ],
                [
                    {
                        'title': 'Introduction to NumPy',
                        'explanation': 'NumPy is a Python library used for numerical computing. It provides arrays and mathematical operations that are useful when working with numeric data. NumPy can perform operations on many values efficiently.',
                        'tamil': 'NumPy numeric data and calculations handle panna useful Python library.',
                        'example': '''import numpy as np

marks = np.array([80, 85, 90])

print(marks)
print(marks.mean())
print(marks.max())''',
                        'output': '[80 85 90]\n85.0\n90',
                        'note': 'Install NumPy in your Python environment before running the example.'
                    },
                    {
                        'title': 'Working with Pandas',
                        'explanation': 'Pandas helps organize data in rows and columns. A DataFrame is similar to a spreadsheet table. It can be used to inspect, filter and summarize datasets before using them in machine learning.',
                        'tamil': 'Pandas DataFrame spreadsheet maadhiri rows and columns-la data organize pannum.',
                        'example': '''import pandas as pd

df = pd.DataFrame({
    "Name": ["Anu", "Ravi"],
    "Score": [80, 90]
})

print(df)
print(df["Score"].mean())''',
                        'output': 'A two-row table is displayed, followed by the average score 85.0.',
                        'note': 'Pandas and NumPy are commonly used together in data workflows.'
                    },
                    {
                        'title': 'Preparing Data',
                        'explanation': 'Before training a machine learning model, data should be inspected and prepared. This may include checking missing values, removing duplicate records and selecting useful columns. Good data preparation helps produce more reliable analysis.',
                        'tamil': 'Model train panna munnaadi data correct-ah irukka nu check panni prepare pannanum.',
                        'example': '''print(df.isnull().sum())

df = df.drop_duplicates()

print(df.head())''',
                        'output': 'Missing-value counts and the first rows of the cleaned DataFrame are displayed.',
                        'note': 'Always understand why values are missing before deciding how to handle them.'
                    }
                ],
                'Load a small dataset and display its rows and column information.',
                [
                    'Create a NumPy array with five values.',
                    'Calculate the mean using NumPy.',
                    'Create a Pandas DataFrame.',
                    'Display the first rows using head().',
                    'Check missing values using isnull().sum().'
                ],
                [
                    {
                        'question': 'What is NumPy mainly used for?',
                        'options': ['Numerical computing', 'Web page styling', 'Email sending', 'Video editing'],
                        'answer': 'Numerical computing'
                    },
                    {
                        'question': 'Which NumPy function creates an array?',
                        'options': ['np.array()', 'np.table()', 'np.list()', 'np.data()'],
                        'answer': 'np.array()'
                    },
                    {
                        'question': 'Which Pandas object represents a table?',
                        'options': ['DataFrame', 'Variable', 'Function', 'String'],
                        'answer': 'DataFrame'
                    },
                    {
                        'question': 'Which method displays the first rows?',
                        'options': ['head()', 'tail_only()', 'start()', 'show()'],
                        'answer': 'head()'
                    },
                    {
                        'question': 'Why do we prepare data before model training?',
                        'options': ['To improve data quality', 'To change the keyboard', 'To style a webpage', 'To create an email'],
                        'answer': 'To improve data quality'
                    }
                ]
            ),

            4: create_lesson(
                'Machine Learning Fundamentals',
                'Understand the basic ideas behind machine learning.',
                [
                    'What is machine learning?',
                    'Supervised and unsupervised learning',
                    'Features and target values',
                    'Training and testing data',
                    'Understanding model predictions'
                ],
                [
                    {
                        'title': 'What is Machine Learning?',
                        'explanation': 'Machine learning is a field of AI in which computers learn patterns from data to make predictions or decisions. Instead of writing every rule manually, developers train models using example data.',
                        'tamil': 'Machine Learning-la computer example data-la irundhu patterns learn panni prediction panna try pannum.',
                        'example': '''Example:

Input data:
Study Hours: 2, 4, 6
Marks:       50, 70, 90

A model can learn a relationship
between study hours and marks.''',
                        'output': 'The example shows a possible relationship that a model could learn from data.',
                        'note': 'A learned relationship does not guarantee that future predictions will be correct.'
                    },
                    {
                        'title': 'Types of Machine Learning',
                        'explanation': 'Supervised learning uses labeled examples where the expected answer is known. Unsupervised learning works with data that does not have provided labels and tries to discover patterns or groups.',
                        'tamil': 'Supervised learning-la correct answer data-la irukkum. Unsupervised learning-la groups and patterns discover pannum.',
                        'example': '''Supervised example:
Email details -> Spam or Not Spam

Unsupervised example:
Customer records -> Similar groups''',
                        'output': 'The examples show classification using labels and grouping without supplied labels.',
                        'note': 'The right approach depends on the problem and available data.'
                    },
                    {
                        'title': 'Features, Targets and Predictions',
                        'explanation': 'Features are input columns used by a model. A target is the value the model is expected to predict in supervised learning. Data is commonly divided into training and testing sets so model performance can be evaluated on separate examples.',
                        'tamil': 'Features na input information. Target na model predict panna vendiya answer.',
                        'example': '''Features:
Study Hours
Attendance

Target:
Exam Result

Training data -> Used to learn patterns
Testing data -> Used to evaluate predictions''',
                        'output': 'The example identifies two input features and one target value.',
                        'note': 'Testing data should be kept separate from the data used to train the model.'
                    }
                ],
                'Explore a beginner classification dataset and identify its features and target.',
                [
                    'Explain machine learning in your own words.',
                    'Write one supervised learning example.',
                    'Write one unsupervised learning example.',
                    'Identify features and target in a student dataset.',
                    'Explain why data is split into training and testing sets.'
                ],
                [
                    {
                        'question': 'What is machine learning?',
                        'options': ['Learning patterns from data', 'Only designing webpages', 'Managing files manually', 'Creating database tables only'],
                        'answer': 'Learning patterns from data'
                    },
                    {
                        'question': 'Which learning type uses labeled data?',
                        'options': ['Supervised learning', 'Unsupervised learning', 'Manual learning', 'Random learning'],
                        'answer': 'Supervised learning'
                    },
                    {
                        'question': 'What are features?',
                        'options': ['Input information used by a model', 'Only the final answer', 'A website theme', 'A database password'],
                        'answer': 'Input information used by a model'
                    },
                    {
                        'question': 'What is a target?',
                        'options': ['The value to predict', 'The computer name', 'The file format', 'The chart title'],
                        'answer': 'The value to predict'
                    },
                    {
                        'question': 'Why use testing data?',
                        'options': ['To evaluate model performance', 'To change the input keyboard', 'To delete the dataset', 'To create HTML pages'],
                        'answer': 'To evaluate model performance'
                    }
                ]
            ),

            5: create_lesson(
                'Build Beginner-Friendly AI Projects',
                'Apply basic AI concepts in a small project.',
                [
                    'Choose a beginner project idea',
                    'Find and understand a suitable dataset',
                    'Prepare the data',
                    'Train and test a simple model',
                    'Review predictions and explain results'
                ],
                [
                    {
                        'title': 'Choose an AI Project',
                        'explanation': 'A beginner AI project should have a clear purpose and manageable scope. Examples include classifying simple categories or predicting a numeric value from example data. Define the problem before choosing a dataset or model.',
                        'tamil': 'Project start panna munnaadi enna problem solve panna porom nu decide pannanum.',
                        'example': '''Project: Student Result Prediction

Possible inputs:
- Study hours
- Attendance

Possible output:
- Predicted result category''',
                        'output': 'A simple project idea with two example input features and one target.',
                        'note': 'A prediction is only an estimate and should not be treated as a guaranteed result.'
                    },
                    {
                        'title': 'Prepare and Train a Model',
                        'explanation': 'A dataset is inspected and prepared before training. In a supervised learning project, the data is split into training and testing sets. A model learns from the training data, and the testing data is used to evaluate its performance.',
                        'tamil': 'Dataset prepare pannitu training data use panni model learn pannum. Testing data use panni performance check pannuvom.',
                        'example': '''from sklearn.model_selection import train_test_split

# X represents input features
# y represents the target

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)''',
                        'output': 'The dataset is divided into training and testing portions.',
                        'note': 'X and y must be prepared before running this example. Scikit-learn must be installed.'
                    },
                    {
                        'title': 'Evaluate and Explain Results',
                        'explanation': 'After training, evaluate the model using suitable measures for the problem. Classification and regression use different evaluation metrics. Review mistakes and explain what the model can and cannot predict.',
                        'tamil': 'Model result vandha udane correct nu assume panna koodadhu. Performance evaluate panni limitations explain pannanum.',
                        'example': '''# Example classification evaluation
from sklearn.metrics import accuracy_score

predictions = model.predict(X_test)

score = accuracy_score(y_test, predictions)

print("Accuracy:", score)''',
                        'output': 'The program displays an accuracy score for the example classification model.',
                        'note': 'Accuracy alone may not fully describe performance, especially when classes are imbalanced.'
                    }
                ],
                'Plan a simple student result prediction project and identify its input data.',
                [
                    'Write the purpose of your AI project.',
                    'Identify the input features and target.',
                    'Choose a suitable beginner dataset.',
                    'Explain the difference between training and testing data.',
                    'Write a short report about possible model limitations.'
                ],
                [
                    {
                        'question': 'What should be decided before building an AI project?',
                        'options': ['The problem to solve', 'The font color', 'The computer wallpaper', 'The file icon'],
                        'answer': 'The problem to solve'
                    },
                    {
                        'question': 'What is a dataset?',
                        'options': ['A collection of related data', 'A CSS property', 'A web browser', 'A keyboard shortcut'],
                        'answer': 'A collection of related data'
                    },
                    {
                        'question': 'What is training data used for?',
                        'options': ['Teaching the model patterns', 'Styling a website', 'Deleting records', 'Changing file names'],
                        'answer': 'Teaching the model patterns'
                    },
                    {
                        'question': 'What is testing data used for?',
                        'options': ['Evaluating the model', 'Writing CSS', 'Creating a password', 'Formatting a document'],
                        'answer': 'Evaluating the model'
                    },
                    {
                        'question': 'Why should model limitations be explained?',
                        'options': ['To describe what the model may not handle correctly', 'To hide all results', 'To remove the dataset', 'To avoid testing'],
                        'answer': 'To describe what the model may not handle correctly'
                    }
                ]
            )
        }
    }
}


# WEB DEVELOPER, DATA ANALYST AND AI ENGINEER LESSON VIEW

@login_required(login_url='login')
def career_learning_center(request, career_slug, step_number):

    career_data = CAREER_LESSONS.get(career_slug)

    if not career_data or step_number not in career_data['lessons']:
        return redirect('learning_roadmap')

    career_goal = career_data['career']
    lesson = career_data['lessons'][step_number]
    current_step = career_data['steps'][step_number - 1]

    if request.method == 'POST':
        if request.POST.get('action') == 'complete_lesson':

            LessonProgress.objects.update_or_create(
                user=request.user,
                career_goal=career_goal,
                lesson_number=step_number,
                defaults={
                    'is_completed': True,
                    'completed_at': timezone.now(),
                }
            )

            roadmap_progress, created = RoadmapProgress.objects.get_or_create(
                user=request.user,
                career_goal=career_goal,
                defaults={'completed_steps': []}
            )

            completed_steps = roadmap_progress.completed_steps

            if current_step not in completed_steps:
                completed_steps.append(current_step)
                roadmap_progress.completed_steps = completed_steps
                roadmap_progress.save()

            messages.success(
                request,
                'Lesson completed successfully!'
            )

            return redirect(
                'career_learning_center',
                career_slug=career_slug,
                step_number=step_number
            )

    lesson_progress = LessonProgress.objects.filter(
        user=request.user,
        career_goal=career_goal,
        lesson_number=step_number,
        is_completed=True
    ).first()

    return render(
        request,
        'core/career-lesson.html',
        {
            'career_goal': career_goal,
            'career_slug': career_slug,
            'step_number': step_number,
            'lesson': lesson,
            'is_completed': lesson_progress is not None,
        }
    )

# ==========================================
# SKILLBRIDGE  - SEPARATE ADMIN PANEL
# ==========================================

from django.contrib.auth.decorators import user_passes_test


def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None and user.is_superuser:
            auth_login(request, user)
            return redirect('admin_dashboard')

        messages.error(
            request,
            'Invalid admin email or password.'
        )

    return render(request, 'core/admin-login.html')


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):

    students = User.objects.filter(
        is_superuser=False,
        is_staff=False
    ).order_by('-date_joined')

    total_students = students.count()
    active_students = students.filter(is_active=True).count()
    total_assessments = SkillAssessment.objects.count()
    total_roadmaps = RoadmapProgress.objects.count()

    total_completed_lessons = LessonProgress.objects.filter(
        is_completed=True
    ).count()

    recent_students = list(
        students.order_by('-date_joined')[:10]
    )

    for student in recent_students:
        profile = StudentProfile.objects.filter(
            user=student
        ).first()

        student.phone_number = (
            profile.phone_number
            if profile and profile.phone_number
            else None
        )
    recent_assessments = SkillAssessment.objects.select_related(
        'user'
    ).order_by('-created_at')[:10]

    recent_logins = students.exclude(
        last_login__isnull=True
    ).order_by('-last_login')[:10]

    recent_activities = ActivityLog.objects.select_related(
        'user'
    ).filter(
        user__is_superuser=False,
        user__is_staff=False
    ).order_by('-created_at')[:30]

    return render(
        request,
        'core/admin-dashboard.html',
        {
            'total_students': total_students,
            'active_students': active_students,
            'total_assessments': total_assessments,
            'total_roadmaps': total_roadmaps,
            'total_completed_lessons': total_completed_lessons,
            'recent_students': recent_students,
            'recent_assessments': recent_assessments,
            'recent_logins': recent_logins,
            'recent_activities': recent_activities,
        }
    )

def admin_logout(request):
    auth_logout(request)
    return redirect('admin_login')
