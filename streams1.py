# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 21:36:38 2020

@author: Ioanna Veizi, Id: 240571
"""

import re 
import json
import glob
import pandas as pd
import matplotlib.pyplot as plt 
from probables import CountMinSketch
import hyperloglog
import math
from sys import exit
from pympler import asizeof # first pip install pympler

print("""Please be patient. A menu of choices will be shown soon.
      Thank you for your comprehension. :) """)

# =============================================================================
# OPEN AND PARSE DATA 
# =============================================================================

files=glob.glob(r"C:\Users\Ioanna\Desktop\streams\twitter_world_cup_1m\\*.json.*") 

for file in files:
    with open(file,encoding="utf8") as f:
        #data=json.load(f)
    
        data= f.readlines()
        
  
        f.close()
        

# =============================================================================
#  CREATE LIST OF TWEETS
# =============================================================================
        
        
list_of_tweets=[] # we create a list of tweets
for i in data :
    list_of_tweets.append(json.loads(i))  


#print("Total number of tweets computed: " , len(list_of_tweets)) #prints the number of tweets ==> 23881



      
"""
def user_ids_dataframe():        
     users_id_dataframe = pd.DataFrame(list_of_tweets)
     data_to_drop= ['filter_level', 'retweeted', 'in_reply_to_screen_name',
                     'possibly_sensitive', 'truncated', 'lang', 'in_reply_to_status_id_str',
                     'in_reply_to_user_id_str', 'in_reply_to_status_id', 'created_at',
                     'favorite_count', 'place', 'coordinates', 'text', 'contributors',
                     'retweeted_status', 'geo', 'source', 'favorited',
                     'in_reply_to_user_id', "entities",'retweet_count', 'user',"id_str"]
     users_id_dataframe.drop(data_to_drop,axis=1,inplace=True)
     return users_id_dataframe

#print(user_ids_dataframe())  

ids_frequency= user_ids_dataframe()["id"].value_counts()
ids_frequency.plot(kind="hist", color="r")
plt.xlabel("Appearance")
plt.ylabel("Number of Ids")
plt.show()
"""


# =============================================================================
# TAGS ANALYSIS
# =============================================================================



chunks = [data[x:x+1000] for x in range(0, len(data), 1000)] # seperate data into chunks
#print(len(chunks))


def tostring(data): #function will be used to find the tags
    str1=""
    for ele in data:
        str1+=ele
    tags=re.findall(r"#(\w+)", str1)
    return tags        
#print(tostring(chunks[1]))


Nested_list_of_tags=[] # create a nested list of tags
for i in chunks:

    Nested_list_of_tags.append(tostring(i))



Tags_output = [] # the list of tags
  

def reemovNestings(l):  #function will remove the nested lists
    for i in l: 
        if type(i) == list: 
            reemovNestings(i) 
        else: 
            Tags_output.append(i) 
  

reemovNestings(Nested_list_of_tags) 
#print ('The list of tags: ', Tags_output) 




Tags_dataframe = pd.Series( Tags_output) #creates a serie containing all found tags
Total_unique_tags=Tags_dataframe.nunique()
#print("Total number of Tags: " , len(Tags_output)) # prints the total number of found tags ==>28606
#print("Total number of unique Tags: ",Tags_dataframe.nunique())# prints the number of unique tags ==> 6299

freq_tags = Tags_dataframe.value_counts() # shows how many times each tag showed

most_frequent_tags=freq_tags.head(30)
#print(freq_tags.head(30)) # shows the 30 most frequent tags 

#visualization of 30 most frequent appeared tags 
def visualise_tags():
    most_frequent_tags.plot(color="green",kind="bar",legend=None)
    plt.xlabel("TAGS")
    plt.ylabel("APPEARANCE")
    plt.title("30 MOST FREQUENT TAGS")
    plt.show()

#print(visualise_tags())
#save showed tags in a csv file 
#freq_tags.reset_index().to_csv(r'C:\Users\Ioanna\Desktop\STREAM_CODE\tags-counter.csv')

Tags_used_memory=freq_tags.memory_usage(deep=True)
#print(Tags_used_memory)

# =============================================================================
# COUNTMINSKETCH FOR TAGS 
# =============================================================================

def countmin(p):

    cms = CountMinSketch(confidence=0.99, error_rate=0.0001)
    
    d={}
    
    
    for r in p:  
            if not d.get(r):
                d[r] = 0
            d[r] += 1
            cms.add(r)
            
        #calculate accuracy    
    True_predictions1=[] 
    List_of_exact_counters=[]
    List_of_approx_counters=[]
    for k,v in d.items():
        List_of_exact_counters.append(v)
        List_of_approx_counters.append(cms.check(k))

    for i in range(len(List_of_exact_counters)):
        if List_of_exact_counters[i]==List_of_approx_counters[i]:
            True_predictions1.append(1)

    True_predictions=True_predictions1.count(1)
    Accuracy= True_predictions/len(List_of_exact_counters)
    
    
    
    
    print('Exact/approx counters')
    for (k, v) in d.items():
        print('{0}: {1:3d}/{2}'.format(k, v, cms.check(k)))
    
    
    
    print( "\nAccuracy of Count-Min Sketch:", Accuracy)
    
    print( "\nConsumed Memory:\n",asizeof.asized(cms, detail=1).format()) #calculates the memory that cms consumes
#print(countmin(Tags_output))



    
# =============================================================================
# HYPERLOGLOG FOR TAGS  
# =============================================================================

def Hyperlog(z,n):


    card= 0
    Hll = hyperloglog.HyperLogLog(0.02)
    
    for i in z:
        card+=1
        Hll.add(str(i))
        
        
        
    print('\nActual Cardinality: {0}'.format(card)) 
    print('Estimated Cardinality: {0}'.format(math.ceil(Hll.card())))


    Accuracy= (math.ceil(Hll.card()))/n #calculate accuracy
    
    print("\nAccuracy of Hyperloglog:",Accuracy)
    print( "\nConsumed Memory:\n",asizeof.asized(Hll, detail=1).format()) #calculates the memory Hll consumes
#print(Hyperlog(Tags_output,Total_unique_tags))


# =============================================================================
# USERS' ANALYSIS
# =============================================================================

def users_tostring(data): #function searching for all mentioned users
    str1=""
    for ele in data:
        str1+=ele
    tags=re.findall(r"@([A-Za-z0-9_]+)", str1)
    return tags 
            
#print(users_tostring(chunks[1]))


List_of_users=[]  # we create a nested list of all mentioned users
for i in chunks:

    List_of_users.append(users_tostring(i))

  

mentioned_users_output= [] # the list of found users
   
def removeNestedLists(l): # function used to remove the nested lists
    for i in l: 
        if type(i) == list: 
            removeNestedLists(i) 
        else: 
            mentioned_users_output.append(i) 
  
removeNestedLists(List_of_users) 
#print ('List of mentioned Users: ', mentioned_users_output) 


users_df = pd.Series( mentioned_users_output) # creates a Serie of mentioned users
Total_unique_users=users_df.nunique()
#print("Total number of mentioned users:", len(mentioned_users_output)) # Total number of mentioned users ==> 48434
#print("Total number of unique users: ", users_df.nunique()) # Total number of unique users ==> 7279

users_frequency = users_df.value_counts()# shows how many times each user showed
most_frequent_users= users_frequency.head(30)
#print(most_frequent_users) # shows the 30 most frequent users


#visualization of 30 most frequent appeared tags 
def visualise_users():
    most_frequent_users.plot(color="green",kind="bar",legend=None)
    plt.xlabel("USERS")
    plt.ylabel("APPEARANCE")
    plt.title("30 MOST FREQUENT USERS")
    plt.show()
#print(visualise_users())

#Save users to a csv file
#users_frequency.reset_index().to_csv(r'C:\Users\Ioanna\Desktop\STREAM_CODE\user-counter.csv')

Users_memory_usage= users_frequency.memory_usage(deep=True)
#print(Users_memory_usage)

# =============================================================================
# COUNTMINSKETCH FOR USERS 
# =============================================================================

#print(countmin( mentioned_users_output))

    
# =============================================================================
# HYPERLOGLOG FOR USERS
# =============================================================================


#print(Hyperlog(mentioned_users_output,Total_unique_users))


def return_menu():
    print("PROCESS COMPLETED")
    key=input("ENTER ANYTHING TO RETURN TO MAIN MENU:")
    print(menu())
       




def menu():
    print("MENU OF CHOICES\n")
    print("1.TAGS' ANALYSIS")
    print("2.SHOW 30 MOST FREQUENT TAGS")
    print("3.COUNT-MIN SKETCH, SIZE AND ACCURACY RESULTS FOR TAGS")
    print("4.HYPERLOGLOG, SIZE AND ACCURACY RESULTS FOR TAGS\n")
    print("5.USERS' ANALYSIS")
    print("6.SHOW 30 MOST FREQUENT USERS")
    print("7.COUNT-MIN SKETCH,SIZE AND ACCURACY FOR USERS")
    print("8.HYPERLOGLOG, SIZE AND ACCURACY RESULTS FOR USERS\n")    
    print("9.QUIT")
    
    while True:
        try:
    
            selection=int(input("ENTER THE NUMBER OF YOUR CHOICE FROM 1-9:"))
            if selection==1:
                print("Total number of Tags: " , len(Tags_output)) 
                print("Total number of unique Tags: ",Tags_dataframe.nunique())
                return_menu()
                break
            elif selection==2:
                print(freq_tags.head(30))
                print(visualise_tags())
                return_menu()
                break
            elif selection==3:
                print(countmin(Tags_output))
                return_menu()
                break
            elif selection==4:
                print(Hyperlog(Tags_output,Total_unique_tags))
                return_menu()
                break
            elif selection==5:
                print("Total number of mentioned users:", len(mentioned_users_output))
                print("Total number of unique users: ", users_df.nunique())
                return_menu()
                break
            elif selection==6:
                print(most_frequent_users)
                print(visualise_users())
                return_menu()
                break
            elif selection==7:
                print(countmin( mentioned_users_output))
                return_menu()
                break
            elif selection==8:    
                print(Hyperlog(mentioned_users_output,Total_unique_users))
                return_menu()
                break
            elif selection==9:
                exit()
            else:
                print("INVALID CHOICE. PLEASE CHOOSE NUMBERS 1-9")
                return_menu()
        except ValueError:
            print("INVALID CHOICE. PLEASE CHOOSE NUMBERS 1-9")
                
        exit()        
print(menu())


       