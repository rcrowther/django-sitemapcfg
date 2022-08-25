from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
from django.apps import apps
#from requests.compat import urljoin



class Command(BaseCommand):
    help = 'Create/update sitemaps'
        
    def get_model(self, model_path):
        Model = None
        if (model_path):
            model_path_elements = model_path.split('.', 1)
            if (len(model_path_elements) != 2):
                raise CommandError("Unable to parse model path (must be form 'app.model'): '{}'".format(model_path))        
            an = model_path_elements[0]
            mn = model_path_elements[1]
            try:
                Model = apps.get_model(an, mn)
            except Exception as e:
                raise CommandError("Unable to locate model from path: '{}'".format(model_path))
        return Model


    # Util
    def normalise_domain(self, domain):
        if (domain[-1] == '/'):
            domain = domain[:-1]
        return domain
        
    def mk_filepath(self, filedir, filename):
        filenameExt = filename + '.xml'
        return Path(filedir) / filenameExt

    def write_xml_header(self, f):
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')


    # Index
    def open_index(self, sitemap_dir, filename):
        filenameExt = Path(sitemap_dir) / (filename + '.xml')
        f = open(filenameExt, "w")
        self.write_xml_header(f)
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        return f
                
    def close_index(self, f):
        f.write('</sitemapindex>')
        f.close()

    def write_index_url(self, f, domain, mapname):
        filenameExt = mapname + '.xml'
        url = domain + '/' + filenameExt
        f.write('    <sitemap><loc>' + str(url) + '</loc></sitemap>\n')


    # sitemaps
    def open_sitemap(self, filepath):
        f = open(filepath, "w")
        self.write_xml_header(f)        
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">\n')
        return f

    def close_sitemap(self, f):
        f.write('</urlset>')
        f.close()
        
    def get_priority(self, entryCfg):
        priority = ''
        if ('priority' in entryCfg):
            priority = entryCfg['priority']
            if (float(priority) > 1):
                raise CommandError(f'Entry has priorty greater than 1: {entry_data}')
        return priority

    def write_sitemap_url(self, f, url, priority):
        f.write('    <url><loc>' + str(url) + '</loc>')
        if (priority):
            f.write('<priority>' + str(priority) + '</priority>')
        f.write('</url>\n')
        
    def write_urls(self, f, entryCfg, domain, priority):
        model_form = 'model' in entryCfg
        literal_form = 'urls' in entryCfg
        if (not(model_form) and not(literal_form)):
            raise CommandError(f"URL config no enties with 'model' or 'url' fields: {entryCfg}")

        b = []
        count = 0
        if (model_form):
            # Model based config
            Model = self.get_model(entryCfg['model'])
            
            #! check has ''field'
            if ('field' in entryCfg):
                # Ok, field based URL construction
                if (not ('url_path' in entryCfg)):
                    raise CommandError(f'Entry config has key for model but no key for url_path: {entryCfg}')
                url_path = entryCfg['url_path']
                r = Model.objects.values_list(entryCfg['field'], flat=True)
                for e in r:
                    url = domain + '/' + url_path + '/' + str(e)
                    self.write_sitemap_url(f, url, priority)
                    count += 1
            else:
                # try construction from get_absolute_url()
                r = Model.objects.all()
                for e in r:
                    url = str(domain) + e.get_absolute_url()
                    self.write_sitemap_url(f, url, priority)
                    count += 1
        if (literal_form):
            for e in entryCfg['urls']:
                url = e
                if (not(e.startswith('http'))):
                    url = domain + '/' + str(e)
                self.write_sitemap_url(f, url, priority)
                count += 1
        return count
        
                  
    def handle(self, *args, **options):         

        # first check these
        # Errors, no attempt to default
        try:
            sitemap_dir = settings.SITEMAP_DIR
        except AttributeError:
            raise CommandError('The sitemap app requires a setting SITEMAP_DIR.')

        try:
            domain = settings.SITEMAP_DOMAIN
        except AttributeError:
            raise CommandError('The sitemap app requires a setting SITEMAP_DOMAIN.')

        # currentlyly, strip trailing slash
        domain = self.normalise_domain(domain)

        try:
            index_name = settings.SITEMAP_INDEX_NAME
        except AttributeError:
            index_name = 'sitemap_index'

        try:
            mapCfg = settings.SITEMAP
        except AttributeError:
            raise CommandError('The sitemap app requires a setting SITEMAP.')

        if (options['verbosity'] > 0):
            print(f"target dir: {sitemap_dir}" )
            print(f"domain: {domain}" )

        b = []
        count = 0
        indexF = self.open_index(sitemap_dir, index_name)
                            
        for mapname, entry_data in mapCfg.items():
            filepath = self.mk_filepath(sitemap_dir, mapname)
            
            sitemapF = self.open_sitemap(filepath)
            for entryCfg in entry_data:
                priority = self.get_priority(entryCfg)
                count = count + self.write_urls(sitemapF, entryCfg, domain, priority)
            self.close_sitemap(sitemapF)
            
            if (options['verbosity'] > 0):
                print(f"sitemap:{filepath}, count:{count}" )
            count = 0
            
            # update index
            self.write_index_url(indexF, domain, mapname)

        self.close_index(indexF)
        
