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
            # 'url_path' is the intermediate path, so allows custom URL path 
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
            'sitemap_specialist_reviews' : [
                {'model': 'reviews.SongReview'},
                {'model': 'datelists.ProductReviews'},
            ],
        }


#### The lastmod attribute
Most sitemap spec attributes are ignored. Google, and presumably other engines, say they ignore them ('priority' etc.). However, Google recognises, and encourages use of, the 'lastmod' attribute. Add 'lastmod' attributes to models like this,

        SITEMAP = {
            # Can set 'lastmod_field' on model datasets
            # Value is the fieldname to get the modification data from
            # The field is expected to be a Django DateField
            'sitemap_infopages' : [
                {'model': 'infopages.Infopage', 'field' : 'slug', , 'url_path': 'info', 'lastmod_field': 'modified'},
            ],
        }

This assumes the declared model field is a Django 'models.DateField'.

There's another option available. This is because it is possible to change a delivered webpage without changing the model. Instead, templates are changed. As a dramatic example, perhaps templates have been adapted with 'structured data' added, to deliver what Google calls 'search snippets'. Of course,, as time goes by, you would like Google (at least, but maybe Bing, Yandex etc.) to recrawl these pages to deliver the new data, and so the enhanced search listing. So a literal date can be declared, in the form YYYY-MM-DD,

        SITEMAP = {
            # Can set a literal value on 'lastmod_field'
            'sitemap_infopages' : [
                {'model': 'infopages.Infopage', 'field' : 'slug', 'lastmod_field': '2021-12-02'},
            ],

            # can also declare a literal value of 'lastmod_field' one-off URLs. 
            'sitemap_other' : [
                {'urls': ['credits', '', 'https://freefalling.com/'], 'lastmod_field': '2021-12-02'},
            ], 
        }

A thought: I considered a 'today' option, but that would update on every sitemap generation, so is wildly imprecise. And unhelpful to search engines. Also, mass updating of model 'modified' dates is not good for site maintenence, the page is updating, not the model data. A literal date will not be automatic, will need the Django Setting file changing and possibly reverting. Whatever, it leaves model data unaltered, as it should be. Once a search engine has crawled, the setting can be reverted to a model 'modified' field, and pages with no model will use the coded literal date, which is a fair representation.
 



### Generate sitemaps

        ./manage.py mksitemap


### End of...
Said it was simple.
