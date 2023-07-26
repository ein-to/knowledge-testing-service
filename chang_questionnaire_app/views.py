from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm
from django.http import HttpResponse
from django.shortcuts import redirect
from .models import Theme, Question, Answer, Results_details
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import collections
from django.db.models import Count
from django.db.models import Q
from collections import Counter
# Create your views here.

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    request.session.set_expiry(2400)
                    login(request, user)
                    return redirect('index')
                else:
                    return HttpResponse('Учетная запись деактивирована')
            else:
                message = 'Неверный логин или пароль'
                return render(request, 'chang_questionnaire_app/login.html', {'form': form, 'message': message})
    else:
        form = LoginForm()
    return render(request, 'chang_questionnaire_app/login.html', {'form': form})


def index(request):
    if request.user.is_authenticated:
        return render(request, 'chang_questionnaire_app/index.html')
    else:
        return redirect('user_login')

def testing_start(request):
    if request.user.is_authenticated:
        theme_list = Theme.objects.all()
        return render(request, 'chang_questionnaire_app/testing_start.html', {'theme_list': theme_list})
    else:
        return redirect('user_login')

def logout_request(request):
    logout(request)
    return redirect('user_login')

@csrf_exempt
def testing(request, num, theme_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            now = datetime.now()
            now = now.strftime("%Y-%m-%d")
            if num == 0:
                theme = request.POST.get('theme_choice')
                t = Theme.objects.get(theme_name=theme)
                theme_id = t.id
                if Results_details.objects.filter(username=request.user.username, theme=t.id).exists():
                    result = Results_details.objects.filter(username=request.user.username, theme=t.id).order_by('-question_id')[0]
                    question_id = next_question_id(result.question_id, theme_id)
                    num = Results_details.objects.filter(username=request.user.username, theme=t.id).count()
                else:
                    question_id = ''
            else:
                question_id = ''
                t = Theme.objects.get(id=theme_id)
                corrects = 0
                incorrects = 0
                checked_answer = request.POST.getlist('checked_answer')
                question = Question.objects.filter(theme=theme_id)[num-1]
                correct_answers = Answer.objects.filter(question=question.id, correct=True)
                result_detail = Results_details()
                try:
                    r = Results_details.objects.get(username=request.user.username, theme=theme_id, question_id=question.id)
                    print(r)
                except:
                    for ch_ans in checked_answer:
                        for cor_ans in correct_answers:
                            if ch_ans == cor_ans.answer_text:
                                corrects = corrects + 1
                                result_detail.username = request.user.username
                                result_detail.theme = theme_id
                                result_detail.date = now
                                result_detail.question_id = question.id
                                result_detail.correct = True
                            else:
                                incorrects = incorrects + 1
                                result_detail.username = request.user.username
                                result_detail.theme = theme_id
                                result_detail.date = now
                                result_detail.question_id = question.id
                                result_detail.correct = False
                            result_detail.save()
            q_len = Question.objects.filter(theme=theme_id)
            if num < len(q_len):
                if question_id:
                    question = Question.objects.get(id=question_id)
                    question_text = question.question_text
                else:
                    question = Question.objects.filter(theme=theme_id)[num]
                    question_id = question.id
                    question_text = question.question_text
                num = num + 1
                command = 'ОК. Далее'
                answers = Answer.objects.filter(question=question_id)
                if num == len(q_len):
                    command = 'Завершить'
                return render(request, 'chang_questionnaire_app/testing_template.html', {'question_text': question_text, 'num': num, 'answers': answers,
                                'theme_id': theme_id, 'command': command, 'theme_name': t.theme_name})
            elif num == len(q_len):
                theme = Theme.objects.get(id=theme_id)
                return render(request, 'chang_questionnaire_app/finish_testing_template.html', {'theme_name': theme.theme_name})
    else:
        return redirect('user_login')

def results(request):
    if request.user.is_authenticated:
        result_type = request.GET.get('result_type')
        themes = Theme.objects.all().order_by('id')
        if result_type == '1':
            data_general = {}
            usernames = Results_details.objects.order_by('username').values('username').distinct()
            for username in usernames:
                data = {}
                for theme in themes:
                    subdata = {}
                    try:
                        correct_amount = Results_details.objects.filter(username=username['username'], theme=theme.id, correct=1).count()
                        incorrect_amount = Results_details.objects.filter(username=username['username'],theme=theme.id, correct=0).count()
                        subdata['correct'] = correct_amount
                        subdata['incorrect'] = incorrect_amount
                    except:
                        pass
                    data[theme.theme_name] = subdata
                data_general[username['username']] = data
            return render(request, 'chang_questionnaire_app/results.html', {'data_general': data_general, 'themes': themes})
        elif result_type == '2' or result_type == '5':
            data_details = []
            if result_type == '2':
                results = Results_details.objects.all().order_by('username', 'theme', 'question_id')
            else:
                results = Results_details.objects.filter(username=request.user.username).order_by('username', 'theme', 'question_id')
            for res in results:
                sublist = []
                theme_name = Theme.objects.get(id=res.theme)
                question = Question.objects.get(theme_id=res.theme, id=res.question_id)
                answer = Answer.objects.get(question_id=res.question_id, correct=1)
                if res.correct == False:
                    correct = 'НЕТ'
                else:
                    correct = 'ДА'
                sublist.append(res.username)
                sublist.append(theme_name.theme_name)
                sublist.append(question.question_text)
                sublist.append(correct)
                sublist.append(answer.answer_text)
                data_details.append(sublist)
            return render(request, 'chang_questionnaire_app/results.html', {'data_details': data_details})
        elif result_type == '3':
            data_incorrect_general = {}
            for theme in themes:
                sum = 0
                result = Results_details.objects.filter(theme=theme.id, correct=0).count()
                data_incorrect_general[theme.theme_name] = result
            return render(request, 'chang_questionnaire_app/results.html', {'data_incorrect_general': data_incorrect_general})
        elif result_type == '4':
            data_incorrect_details = {}
            for theme in themes:
                subdata = {}
                count_list = []
                result = Results_details.objects.filter(theme=theme.id, correct=0).order_by('question_id')
                for res in result:
                    question = Question.objects.get(id=res.question_id)
                    count_list.append(question.question_text)
                count_list = dict(Counter(count_list))
                data_incorrect_details[theme.theme_name] = count_list
            return render(request, 'chang_questionnaire_app/results.html', {'data_incorrect_details': data_incorrect_details})
        else:
            return render(request, 'chang_questionnaire_app/results.html')
    else:
        return redirect('user_login')


def next_question_id(question_id, theme_id):
    questions = Question.objects.filter(theme_id=theme_id)
    for q in questions:
        if q.id > question_id:
            question_id = q.id
            break
    return question_id
