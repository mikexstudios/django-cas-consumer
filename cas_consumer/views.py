from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages

__all__ = ['login', 'logout',]

cas_base = settings.CAS_BASE
cas_login = cas_base + settings.CAS_LOGIN_URL
cas_logout = cas_base + settings.CAS_LOGOUT_URL

def login(request):
    """ Fairly standard login view.

        1. Checks request.GET for a service ticket.
        2. If there is NOT a ticket, redirects to the CAS provider's login page.
        3. Otherwise, attempt to authenticate with the backend using the ticket.
        4. If the backend is able to validate the ticket, then the user is
           logged in and redirected to *CAS_NEXT_DEFAULT*.
        5. Otherwise, the process fails and displays an error message.

    """
    ticket = request.GET.get(settings.CAS_TICKET_LABEL, None)
    next = request.GET.get('next', settings.LOGIN_REDIRECT_URL)

    #If CAS_SERVICE setting is not set, automatically set the service url based
    #on request host. Since we don't provide a location, it will automatically
    #be set to this login view url along with all query strings.
    service = getattr(settings, 'CAS_SERVICE', request.build_absolute_uri())

    if ticket is None:
        params = settings.CAS_EXTRA_LOGIN_PARAMS
        params.update({settings.CAS_SERVICE_LABEL: service})
        url = cas_login + '?'
        raw_params = ['%s=%s' % (key, value) for key, value in params.items()]
        url += '&'.join(raw_params)
        return redirect(url)
    user = authenticate(service=service, ticket=ticket)
    if user is not None:
        auth_login(request, user)
        name = user.first_name or user.username
        messages.success(request, 'Login successful.')
        return redirect(next)
    else:
        messages.error(request, 'Error authenticating with CAS.')
        return redirect(next)

def logout(request, next_page = settings.CAS_REDIRECT_ON_LOGOUT):
    """ Logs the current user out. If *CAS_COMPLETELY_LOGOUT* is true, redirect
    to the provider's logout page, which will redirect to ``next_page``.

    """
    auth_logout(request)
    if settings.CAS_COMPLETELY_LOGOUT:
        return redirect('%s?url=%s' % (cas_logout, next_page))
    return redirect(next_page)
