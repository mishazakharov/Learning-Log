from django.shortcuts import render,get_object_or_404
from .models import Topic,Entry
from django.http import HttpResponseRedirect,Http404
from django.core.urlresolvers import reverse
from .forms import TopicForm,EntryForm
from django.contrib.auth.decorators import login_required
 
# Create your views here.
def check_topic_owner(topic,request):
	if topic.owner != request.user:
		raise Http404

def index(request):
	'''Домашняя страница приложения.'''
	return render(request,'learning_logs/index.html')

@login_required
def topics(request):
	'''Выводит список тем.'''
	topics = Topic.objects.filter(owner=request.user).order_by('date_added')
	context = {'topics':topics}
	return render(request,'learning_logs/topics.html',context)

@login_required
def topic(request,topic_id):
	'''Выводит тему и все записи о ней.'''
	topic = get_object_or_404(Topic,id=topic_id)
	# Проверка того, что тема принадлежит текущему пользователю.
	check_topic_owner(topic,request)
	entries = topic.entry_set.order_by('-date_added')
	context = {'topic':topic,'entries':entries}
	return render (request,'learning_logs/topic.html',context)

@login_required
def new_topic(request):
	'''Определяет новую тему.'''
	if request.method != 'POST':
		# Данные не отправлялись, создается пустая форма.
		form = TopicForm()
	else:
		# Отправляет данные POST, обработать данные.
		form = TopicForm(request.POST)
		if form.is_valid():
	 		new_topic = form.save(commit=False)
	 		new_topic.owner = request.user
	 		new_topic.save()
	 		return HttpResponseRedirect(reverse('learning_logs:topics'))
	context = {'form':form}
	return render(request,'learning_logs/new_topic.html',context)

@login_required
def new_entry(request,topic_id):
	'''Добавляет новую запись по заданной теме.'''
	topic = Topic.objects.get(id=topic_id)
	if request.method != 'POST':
		# Данные не отправлялись, создается пустая форма.
		form = EntryForm()
	else:
		# Отправляет данные POST, обработать данные.
		form = EntryForm(data=request.POST)
		if form.is_valid():
			new_entry = form.save(commit=False)
			new_entry.topic = topic
			new_entry.save()
			return HttpResponseRedirect(reverse('learning_logs:topic',
														args=[topic_id]))
	context = {'topic':topic,'form':form}
	return render(request,'learning_logs/new_entry.html',context)

@login_required
def edit_entry(request,entry_id):
	'''Редактирует сущетсвующиую запись.'''
	entry = Entry.objects.get(id=entry_id)
	topic = entry.topic
	check_topic_owner(topic,request)
	if request.method != 'POST':
		# Исходный запрос, форма заполняется текущими данными!
		form = EntryForm(instance=entry)
	else:
		# Отправка данных POST, обработать данные.
		form = EntryForm(instance=entry,data=request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('learning_logs:topic',args=[topic.id]))
	context = {'entry':entry,'topic':topic,'form':form}
	return render(request,'learning_logs/edit_entry.html',context)



