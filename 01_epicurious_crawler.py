############### IMPORTS #################

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pickle
import json
import multiprocessing as mp
from collections import defaultdict as dd
from datetime import datetime as dt


############# RECIPE CLASS ##############

class Recipe: 
    
    #build recipe object from page
    def __init__(self, page, url):
        
        self.title = self.get_title(page)
        self.url = url
        self.categories = self.get_categories(page)
        self.desc = self.get_desc(page) 
        self.date = self.get_date(page)
        self.image_link = self.get_image_link(page)
        self.rating = self.get_rating(page)
        self.recomm_perc = self.get_recomm_perc(page)
        self.ingredients = self.get_ingredients(page)
        self.nutrients = self.get_nutrients(page)
        self.preparation = self.get_preparation(page)
        self.preparation_note = self.get_chef_note(page)
        self.servings = self.get_servings(page)
        
    #getters  
    def get_title(self, page): 
        return page.find('h1', {'itemprop': 'name'}).text.strip()
    
    def get_date(self, page):
        try:
            return page.find('meta', {'itemprop': 'datePublished'})['content']
        except:
            return None
    
    def get_image_link(self, page): 
        try: 
            return page.find('img', {'class': 'photo loaded'})['srcset']
        except: 
            return None
    
    def get_rating(self, page):
        try:
            return float(page.find('span', {'class': 'rating'}).text.split('/')[0]) * 5 / 4
        except:
            return None
    
    def get_recomm_perc(self, page):
        try:
            return float(page.find('div', {'class': 'prepare-again-rating'}).find('span').text[:-1])
        except:
            return None

    def get_desc(self, page):
        try:
            return page.find('div', {'itemprop': 'description'}).find('p').text.strip()
        except:
            return None

    def get_ingredients(self, page):
        return self.get_grouped_data(page, 'ingredient-group')
    
    def get_preparation(self, page):
        return self.get_grouped_data(page, 'preparation-group')
    
    def get_chef_note(self, page):
        try:
            return page.find('div', {'class': 'chef-notes-content'}).text.strip()
        except: 
            return None
    
    def get_servings(self,page): 
        try:
            return int(page.find_all('span',{'class':'per-serving'})[0].text.split(" ")[2][1:])
        except: 
            return None
    
    def get_nutrients(self,page):
        return self.get_nutridata(page)
            
    def get_categories(self, page):
        return self.get_category_data(page)
    
    
    #helpers
    def get_grouped_data(self, page, group):
        
        groups = page.find_all('li', {'class': group})
        
        if len(groups) == 1:
            return [i.text.strip() for i in groups[0].find_all('li')]

        else:  
            results = []
            for i,g in enumerate(groups):
                try: 
                    group_title = g.find('strong').text.strip(":")
                except: 
                    group_title = "Group {}".format(i+1)
                group_content = [i.text.strip() for i in g.find_all('li')]
                results.append({group.replace("-","_"): group_title, 
                                group+"-content".replace("-","_"): group_content})
            return results

        
    def get_nutridata(self, page): 
        
        nutri_data = page.find_all('span', {'class':'nutri-data'}) 
        
        if len(nutri_data) == 0: 
            return None
        else: 
            nutrients = ["calories", "carbohydrates", "fat", "protein", "saturated_fat", 
                         "sodium", "poly_fat","fiber",  "mono_fat", "cholesterol"]
            list_of_10 = [float(n.text.split(" ")[0]) if len(n.text) > 1 else None 
                          for n in nutri_data]
            return {k:v for k,v in zip(nutrients,list_of_10)}
        

    def get_category_data(self, page):
        
        category_dict = dd(list)
        
        try:
            for tag in page.find('dl', {'class': 'tags'}):
                category_dict["{}".format(tag["href"].split("/")[1])].append(tag.text)
            return category_dict
        except: 
            return None

        
############ MAIN FUNCTIONS #############

#logs entry
def log_entry(url,e): 
    with open('logs/crawler_log.txt', 'a') as logs: 
        logs.write("{} - Error at URL {}: {}\n".format(str(dt.now()), url, str(e)))

#takes a list and outputs even chunks
def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

#builds recipes
def build_recipes(job_id, end_urls_slice):
    
    slice_recipes = []
    for url in end_urls_slice:

        print('Working on recipe: {}'.format(url))
        try: 
            #process html
            page_html = urlopen(url)
            page = bs(page_html, 'html.parser')

            #build & append object 
            recipe = Recipe(page, url)
            slice_recipes.append(recipe.__dict__)
        
        except Exception as e: 
            log_entry(url, e)
            continue
    
    #dumps one list for every process 
    with open('pickle/recipe_batch_{}.pkl'.format(job_id), 'wb') as f:
        pickle.dump(slice_recipes, f)
    

#handles multiprocessing 
def handle_jobs(data, job_no):
    total = len(data)
    chunk_size, chunk_mod = (int(total / job_no), total % job_no)
    if chunk_mod != 0: 
        data = data[:-chunk_mod]
    slices = chunks(data, chunk_size)
    jobs = []
        
    for i, s in enumerate(slices):
        j = mp.Process(target=build_recipes, args=(i, s))
        jobs.append(j)
    for j in jobs:
        j.start()
    for j in jobs: 
        j.join()    

#main
def main(processes): 
    
    #run all jobs 
    end_urls = pickle.load(open("pickle/recipe_urls.pkl", "rb"))
    handle_jobs(end_urls, processes)
    
    #merge all process data
    recipes_final = []
    for i in range(processes):
        recipes_final += pickle.load(open("pickle/recipe_batch_{}.pkl".format(i), "rb"))
    
    #dumps final recipes
    print('Total Recipes: ', len(recipes_final))
    with open('data/recipe_urls.json', 'w') as f:
        json.dump(recipes_final, f)

                             
################ MAIN ###################

if __name__ == '__main__':
    #to be adjusted for processes
    main(16)
