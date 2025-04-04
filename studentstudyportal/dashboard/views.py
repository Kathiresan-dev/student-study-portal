from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from . forms import *
from . models import Notes,Homework
from django.contrib import messages
from django.views import generic
from django.utils import timezone
import datetime,requests,wikipedia
from youtubesearchpython import VideosSearch


# Create your views here.
def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes(request,pk=None):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully!")
    else:
        form = NotesForm()    
        
    form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes
    
@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            
            finished = request.POST.get('is_finished', 'off') == 'on'

            
            due_str = request.POST.get('due', '').strip()
            if due_str:
                try:
                    due = timezone.make_aware(datetime.datetime.strptime(due_str, "%Y-%m-%d"))
                except ValueError:
                    messages.error(request, "Invalid due date format!")
                    return redirect('homework') 
            else:
                due = None 

            
            homeworks = Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=due,
                is_finished=finished
            )
            homeworks.save()
            
            messages.success(request, f'Homework Added from {request.user.username}!')
            form = HomeworkForm() 

    else:
        form = HomeworkForm()
    homeworks = Homework.objects.filter(user=request.user)
    if len(homeworks) == 0:
        homeworks_done = True
    else:
        homeworks_done = False
    homeworks = zip(homeworks, range(1, len(homeworks)+1))
    context = {'form': form, 'homeworks': homeworks,
            'homeworks_done': homeworks_done}
    return render(request, 'dashboard/homework.html', context)

@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('homework')

@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('homework')

def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict = {
                'input': text,
                'title': i.get('title', 'No Title'),
                'duration': i.get('duration', 'N/A'),
                'thumbnail': i['thumbnails'][0]['url'] if 'thumbnails' in i and i['thumbnails'] else 'https://via.placeholder.com/150',
                'channel': i['channel']['name'] if 'channel' in i and 'name' in i['channel'] else 'Unknown',
                'link': i.get('link', '#'),
                'views': i['viewsCount']['short'] if 'viewsCount' in i and 'short' in i['viewsCount'] else 'No Views',
                'published': i.get('publishedTime', 'Unknown')
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc 
            result_list.append(result_dict)
            context = {
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)    
    else:
        form = DashboardForm()    
    context = {'form':form}
    return render(request,"dashboard/youtube.html",context)

@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user=request.user, title=request.POST['title'], is_finished=finished)
            todos.save()
            messages.success(request,f"Todo Added from {request.user.username}!!")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0 :
        todos_done = True
    else:
        todos_done = False
    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,"dashboard/todo.html",context)

@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')

@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    if 'profile' in request.META['HTTP_REFERER']:
        return redirect('profile')
    return redirect('todo')

import requests

def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        

        url = f"https://www.googleapis.com/books/v1/volumes?q={text}"
        response = requests.get(url)
        data = response.json()

        result_list = []
        if "items" in data:
            for item in data["items"]:
                volume_info = item.get("volumeInfo", {})
                result_dict = {
                    'input': text,
                    'title': volume_info.get('title', 'No Title'),
                    'authors': ", ".join(volume_info.get('authors', ['Unknown'])),
                    'publisher': volume_info.get('publisher', 'Unknown'),
                    'thumbnail': volume_info['imageLinks']['thumbnail'] if 'imageLinks' in volume_info else 'https://via.placeholder.com/150',
                    'description': volume_info.get('description', 'No description available'),
                    'link': volume_info.get('infoLink', '#'),
                    'published': volume_info.get('publishedDate', 'Unknown')
                }
                result_list.append(result_dict)
                context = {
                    'form': form,
                    'results': result_list
                }
        return render(request, 'dashboard/books.html', context)
    else:
        form = DashboardForm()    
    context = {'form': form}
    return render(request, "dashboard/books.html", context)


def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST.get('text', '').strip()

        if not text:
            return render(request, "dashboard/dictionary.html", {'form': form, 'error': "Please enter a word to search."})

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{text}"

        try:
            r = requests.get(url)
            r.raise_for_status()

            answer = r.json()

            if not answer or isinstance(answer, dict):
                raise Exception(f"No definition found for '{text}'.")

            # Extracting data safely
            phonetics = answer[0].get('phonetics', [{}])[0].get('text', 'N/A')
            audio = answer[0].get('phonetics', [{}])[0].get('audio', '')

            definition_data = answer[0].get('meanings', [{}])[0].get('definitions', [{}])[0]
            definition = definition_data.get('definition', 'No definition available')
            example = definition_data.get('example', 'No example available')
            synonyms = definition_data.get('synonyms', [])

            if not synonyms:
                synonyms = ["No synonyms available"]

            context = {
                'form': form,
                'input': text,
                'phonetics': phonetics,
                'audio': audio,
                'definition': definition,
                'example': example,
                'synonyms': synonyms
            }

        except requests.exceptions.RequestException as e:
            context = {'form': form, 'error': f"Error fetching data: {e}"}
        except Exception as e:
            context = {'form': form, 'error': str(e)}

        return render(request, "dashboard/dictionary.html", context)

    else:
        form = DashboardForm()

    return render(request, "dashboard/dictionary.html", {'form': form})



def wiki(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        form = DashboardForm(request.POST)
        
        try:
            search = wikipedia.page(text) 
            context = {
                'form': form,
                'title': search.title,
                'link': search.url,
                'details': search.summary,
            }
        except wikipedia.exceptions.DisambiguationError as e:
            context = {
                'form': form,
                'title': "Multiple Results Found",
                'details': f"Did you mean: {', '.join(e.options[:5])}?", 
            }
        except wikipedia.exceptions.PageError:
            context = {
                'form': form,
                'title': "Page Not Found",
                'details': "No Wikipedia page found for the given search term.",
            }
        except Exception as e:
            context = {
                'form': form,
                'title': "Error",
                'details': f"An error occurred: {str(e)}",
            }

        return render(request, "dashboard/wiki.html", context)

    form = DashboardForm()
    context = {'form': form}
    return render(request, "dashboard/wiki.html", context)



def conversion(request):
    form = ConversionForm()
    context = {'form': form, 'input': False, 'm_form': None}

    if request.method == "POST":
        form = ConversionForm(request.POST)
        if form.is_valid():
            measurement = form.cleaned_data['measurement']

            measurement_form = None

            if measurement == 'length':
                measurement_form = ConversionLengthForm(request.POST)
            elif measurement == 'mass':
                measurement_form = ConversionMassForm(request.POST)

            context.update({'m_form': measurement_form, 'input': True})

            answer = ""
            if measurement_form and 'value' in request.POST:
                first = request.POST.get('measure1')
                second = request.POST.get('measure2')
                input_value = request.POST.get('value')

                if input_value and float(input_value) >= 0:
                    input_value = float(input_value)

                    if first == 'Yard' and second == 'Foot':
                        answer = f'{input_value} Yard = {input_value * 3} Foot'
                    elif first == 'Foot' and second == 'Yard':
                        answer = f'{input_value} Foot = {input_value / 3} Yard'
                    elif first == 'Pound' and second == 'Kilogram':
                        answer = f'{input_value} Pound = {input_value * 0.453592} Kilogram'
                    elif first == 'Kilogram' and second == 'Pound':
                        answer = f'{input_value} Kilogram = {input_value * 2.20462} Pound'

            context['answer'] = answer

    print("DEBUG: Context being passed to template ->", context)  

    return render(request, "dashboard/conversion.html", context)

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username}")
            return redirect("home")
            
    else:        
        form = UserRegisterForm()
    context = {
        'form':form
    }
    return render(request,"dashboard/register.html",context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished = False,user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False  
    if len(todos) == 0:
        todo_done = True
    else:
        todo_done = False  
    context = {
        'homeworks' : homeworks,
        'todos' : todos,
        'homework_done' : homework_done,
        'todo_done' : todo_done
    }
    return render(request,"dashboard/profile.html",context)


