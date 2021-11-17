from django.shortcuts import render,redirect
import calendar,csv
from django.http import HttpResponseRedirect,HttpResponse,FileResponse
from datetime import datetime
from .models import Event,Venue
from .forms import VenueForm,EventForm,EventFormAdmin
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User

def my_events(request):
    if request.user.is_authenticated:
        events = Event.objects.filter(attendees=request.user.id)
        return render(request,'events/my_events.html',{
            'events':events
            })
    else:
        messages.success(request,'Your are not allowed!')
        return redirect('home')

def venues_pdf(request):
    venues = Venue.objects.all()

    buf = io.BytesIO()

    c = canvas.Canvas(buf,pagesize=letter,bottomup=0)
    txtob = c.beginText()
    txtob.setTextOrigin(inch,inch)
    txtob.setFont("Helvetica",14)

    lines = []
    for venue in venues:
        lines.append(f'Venue Name:{venue.name}')
        lines.append(f"Address:{venue.address}")
        lines.append(f"Zip-code:{venue.zip_code}")
        lines.append(f"Phone-number:{venue.phone_number}")
        lines.append(f"Web-address:{venue.web}")
        lines.append(f"Email-address:{venue.email_address}")
        lines.append("__________________________________")
        lines.append(" ")

    for line in lines:
        txtob.textLine(line)

    c.drawText(txtob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf,as_attachment=True,filename="venues.pdf")

def venues_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'

    writter = csv.writer(response)

    venues = Venue.objects.all()

    writter.writerow(['Venue name','Address','Zip-code','Phone-number','Web-address','Email-address'])

    for venue in venues:
        writter.writerow([venue.name,venue.address,venue.zip_code,venue.phone_number,venue.web,venue.email_address])

    return response

def venues_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'
    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(f'Venue Name:{venue.name}\nAddress:{venue.address}\nZip-code:{venue.zip_code}\nPhone-number:{venue.phone_number}\nWeb-address:{venue.web}\nEmail-address:{venue.email_address}\n\n\n\n')

    response.writelines(lines)
    return response

def delete_venue(request,venue_id):
    venue = Venue.objects.get(pk=venue_id)
    if request.user.id == venue.owner or request.user.is_superuser:
        venue.delete()
        messages.success(request,'Venue is deleted successfully!')
        return redirect("venues")
    else:
        messages.success(request, 'You are not the owner of this venue!')
        return redirect("venues")

def delete_event(request,event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager or request.user.is_superuser:
        event.delete()
        messages.success(request, "Event is deleted successfully!")
        return redirect("events")
    else:
        messages.success(request,"You are not manager of this event!")
        return redirect("events")

def update_event(request,event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)

    if form.is_valid():
        form.save()
        messages.success(request, 'Event is updated successfully')
        return redirect("events")

    return render(request, "events/update_event.html", {
        "event":event,
        'form': form,
    })

def add_event(request):
    submitted = False
    if request.method == "POST":
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect("/add_event?submitted=True")
        else:
            form = EventForm(request.POST)

            if form.is_valid():
                event = form.save(commit=False)
                event.manager = request.user
                event.save()
                return HttpResponseRedirect("/add_event?submitted=True")
    else:
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm
        if "submitted" in request.GET:
            submitted = True

    return render(request, 'events/add_event.html', {
        "form": form,
        'submitted': submitted,
    })

def update_venue(request,venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    if request.user.id == venue.owner or request.user.is_superuser:
        form = VenueForm(request.POST or None,instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue is updated successfully!')
            return redirect("venues")

        return render(request,"events/update_venue.html",{
            "venue":venue,
            'form':form,
            'venue_owner':venue_owner
        })
    else:
        messages.success(request,"You are not the owner of this venue!")
        return redirect("venues")

def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)
        events = Event.objects.filter(name__contains=searched)
        return render(request,"events/search.html",{
            "searched":searched,
            "venues":venues,
            "events":events,
            "lenevent":len(events)==0,
            "lenvenue": len(venues) == 0,
        })
    else:
        return render(request, "events/search.html", {})

def show_event(request,event_id):
    event = Event.objects.get(pk=event_id)
    return render(request, "events/show_event.html", {
        "event": event,
    })

def show_venue(request,venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    return render(request,"events/show_venue.html",{
        "venue":venue,
        "venue_owner":venue_owner,
    })

def venues(request):
    #venue_list = Venue.objects.all().order_by('?')
    #venue_list = Venue.objects.all().order_by('-name')

    p = Paginator(Venue.objects.all().order_by('name'),20)
    page = request.GET.get("page")
    venues = p.get_page(page)

    nums = "a"*venues.paginator.num_pages

    return render(request, 'events/venues.html', {
        "len":len(venues)==0,
        'venues':venues,
        'nums':nums,
    })

def add_venue(request):
    submitted = False
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user.id
            venue.save()
            return HttpResponseRedirect("/add_venue?submitted=True")
    else:
        form = VenueForm
        if "submitted" in request.GET:
            submitted = True

    return render(request, 'events/add_venue.html', {
        "form":form,
        'submitted':submitted,
    })

def home(request):
    return render(request, 'events/home.html', {
        "current_year":datetime.now().year,
    })

def cal(request,year=datetime.now().year,month=datetime.now().strftime("%B")):
    month = month.title()
    month_number = int(list(calendar.month_name).index(month))
    cal = calendar.HTMLCalendar().formatmonth(year,month_number)
    now = datetime.now()
    current_year = now.year
    time = now.strftime('%I:%M:%S %p')
    return render(request,'events/cal.html',{
        "cal":cal,
        "current_year":current_year,
        "time":time,
    })

def events(request):
    p = Paginator(Event.objects.all().order_by('event_date'), 20)
    page = request.GET.get("page")
    events = p.get_page(page)

    nums = "a" * events.paginator.num_pages

    return render(request, 'events/events.html', {
        "len": len(events) == 0,
        'events': events,
        'nums': nums
    })