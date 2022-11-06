# SitemapCfg
Django's [sitemap framework](https://docs.djangoproject.com/en/4.1/ref/contrib/sitemaps/) is classic Django. It covers all Django functionality. It's class-based. It's configurable and flexible. It can reverse URLs and ping Google. Most of the time it's exactly what you want, and everything you could want. But not all of the time. Perhaps, like me, you use Django in an unusual way. The sitemap framework is not only difficult to use, it will not do some things I want. So I've made this configuration-based alternative. It's crude, but simple.


## Why you would not want to use this app
- Can only output URLs from model URL data, not views
- Has no exclude/filter configuration, outputs everything
- No checks for sitemap file-size, subfolder renaming etc.
- Creates a sitemap index always, despite one sitemap only
- Ignores most of the sitemap spec
- Can only handle one site

## Why you would want to use this app
- Search engines also ignore most of the spec
- 5 minuite setup in 'settings' file only


## Documentation
### Install
PyPi,

        pip install sitemap_cfg

Or download the app code to Django.

The module needs no database tables, but need to declare so the registered module can find models etc. Declare in Django settings,

        INSTALLED_APPS = [
            ...
            'sitemap_cfg.apps.SitemapCfgConfig',
        ] 

 
### Configuration
Need to declare where the sitemap files will go,

        SITEMAP_DIR = PROJECT_DIR / "static"

The domain (usually set for cannonical),

        SITEMAP_DOMAIN = "https://freefalling.com"

Sitemap index name defaults to 'sitemap_index', but can be renamed,

        SITEMAP_INDEX_NAME = 'sitemap_main'

Then declare which models to use, or URLs to add. Keys are the sitemap filename,

        SITEMAP = {
            # Model names are just the app/model name (not the full path)
            # If model is the only data given, tries to use get_absolute_url()
            'sitemap_reviews' : [
                {'model': 'reviews.Review'},
            ],

            # Can use data from the model to construct URLs, usually a slug
            # 'url_path' is the intermediate parh, so allows custom URL path 
            'sitemap_infopages' : [
                {'model': 'infopages.Infopage', 'field' : 'slug', 'url_path': 'info'},
            ],

            # can also declare one-off URLs. 
            # if preceeded by ''http' these are written as presented...
            # if written as stubs get prepended by SITEMAP_DOMAIN
            'sitemap_other' : [
                {'urls': ['credits', '', 'https://freefalling.com/' ]},
            ], 


            # Can have different collections of data in one sitemap
            'sitemap_netfeatures' : [
                {'model': 'reviews.SongReview'},
                {'model': 'datelists.Itineries'},
            ],

            # Can set 'lastmod_field' on model datasets
            # Value is the fieldname to get the modification data from
            # The field is expected to be a Django DateField
            'sitemap_netfeatures' : [
                {'model': 'infopages.Infopage', 'field' : 'slug', 'lastmod_field': 'modified'},
            ],
        }

Note that, at the time of writing, Google say they recognise only 'lastmod' attritutes in sitemaps.


### Generate sitemaps

        ./manage.py mksitemap


### End of...
Said it was simple.
