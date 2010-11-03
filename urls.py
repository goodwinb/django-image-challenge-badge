from django.conf.urls.defaults import *
from lefty_app.views import *
from lefty.settings import PRODUCTION

# The next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', main_page),
    (r'^add/(?P<image_id>\d+)/(?P<challenge_id>\d+)/$', add_image_to_challenge),
    (r'^challenge/(?P<challenge_id>\d+)/$', challenge),
    (r'^challengeentry/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', challenge_entry),
    (r'^feedback/$', feedback),
    (r'^findchallenges/$', find_challenges),
    (r'^image_upload/$', image_upload),
    (r'^legal/$', legal),
    (r'^lose/(?P<challenge_id>\d+)/$', lose),
    (r'^move/(?P<direction>\w+)/(?P<challenge_image_id>\d+)/$', move),
    (r'^remove/(?P<challenge_image_id>\d+)/$', remove),
    (r'^setup_challenge/$', setup_challenge),
    (r'^setup_challenge_images/(?P<challenge_id>\d+)/$', setup_challenge_images),
    (r'^tag/(\w+)/$', tag_page),
    (r'^user/(\w+)/$', user),
    (r'^vote/(?P<challenge_id>\d+)/(?P<vote>\w+)/$', challenge_vote),
    (r'^win/(?P<challenge_id>\d+)/$', win),

    # Admin and registration URLs
    (r'^admin/', include(admin.site.urls)),
    (r'^signup/$', registration_page),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', logout_page),
    (r'password_reset/$', 'django.contrib.auth.views.password_reset'),
    (r'password_reset_done/$', 'django.contrib.auth.views.password_reset_done'),
    (r'password_reset_confirm/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'password_change/$', 'django.contrib.auth.views.password_change'),
    (r'password_reset_complete/$', 'django.contrib.auth.views.password_reset_complete'),    
)

if PRODUCTION == False:
    import os.path
    site_media = os.path.join(
        os.path.dirname(__file__), 'site_media'
    )
    urlpatterns += patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
     { 'document_root': site_media }),                            
)
