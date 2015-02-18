# -*- coding: cp1252 -*-
import operator
import re, string
import json
import sys

from decimal import *
getcontext().prec = 3




## Category
##  contains:
##      - Name/Title
##      - Associated Tweets
##      - Associated decisions (winner, loser, presenter, nominees, etc.)
class Category:

    # Category(name,decisions)
    #   Set name
    #   Set decisions
    #   Set keys
    def __init__(self,nam,key,n, p):
        self.name = nam
        self.keys = key
        self.tweets = []
        self.nominees  = {}
        self.winners = {}
        self.presenters = p ##Printed
        self.winner = '' ## Printed
        self.nominee = n## Printed

    # addTweet(tweet)
        # Add parsed tweet to two dimensional array
    def addTweet(self,t):
        self.tweets.append(t)

    def addNominees(self,nom):
        for n in nom:
            if n in self.nominees.keys():
                self.nominees[n] += 1
            else:
                self.nominees[n] = 1

    def addWinners(self,win):
        for n in win:
            if n in self.winners.keys():
                self.winners[n] += 1
            else:
                self.winners[n] = 1
    def addPresenters(self,pre):
        for n in pre:
            if n in self.nominees.keys():
                self.nominees[n] += 1
            else:
                self.nominees[n] = 1

    def findPresenters(self):
        return self.presenters

    def findNominees(self):
        return self.nominees

    def findWinner(self):
        try:
            # Check for mispellings
            for a in self.winners:
                for b in self.winners:
                    # Takes all the double names
                    if len(a) == 2 and len(b) == 2 and not a == b and not (self.winners[a] == -1 or self.winners[b] == -1):
                        # If first or last name is the same
                        if a[0] == b[0] or a[1] == b[1]:
                            # Combine
                            if self.winners[b] > self.winners[a]*10:
                                self.winners[a] += self.winners[b]
                                self.winners[b] = -1
                            elif self.winners[a] > self.winners[b]*10:
                                self.winners[b] += self.winners[a]
                                self.winners[a] = -1
                        
    
            # Adds all single name nominees to the double name
            for a in self.winners:
                for b in self.winners:
                    if (''.join(a) in ''.join(b)) and not (a == b):
                        if not self.winners[b] == -1:
                            if self.winners[b] > self.winners[a]*10:
                                self.winners[b] += self.winners[a]
                                self.winners[a] = -1
                        ##else: ## Single word is way more popular
                        ##    if not self.nominees[a] == -1:
                        ##        self.nominees[a] += self.nominees[b]
                        ##        self.nominees[b] = -1
            #print '\n\BEFORE NOMS:'
            #print self.winners  

            # Hardcheck against nominees
            temp = {}
            for a in self.winners:
               for b in self.nominee:
                   if ''.join(a) in ''.join(b):
                       if not b in self.winners:
                           if b not in temp:
                               temp[b] = self.winners[a]
                           else:
                               temp[b]+= self.winners[a]
                       else:
                           self.winners[b] += self.winners[a]
                           
                               
            ### ADD WINNERS
            for t in temp:
                if t in self.winners:
                    self.winners[t] += temp[t]
                else:
                    self.winners[t] = temp[t]
            
            self.winner=max(self.winners.iteritems(), key=operator.itemgetter(1))[0]

            if self.winner in self.nominee:
                self.nominee.remove(self.winner)

            if len(self.winner) == 2:
                self.winner = ' '.join(self.winner)
            #print '\n\nAFTER:'
            #print self.winners            
            return self.winner
        except Exception:
           self.winner = 'No winner added'
           return 'Error. No winner added'


## #################
## Global Structures
## #################

## Global Keys
##  Keys are the words we are searching for
##  The keys I'm using are not refined at all, probably wouldn't work to well
##  Idea - use a dictionary to weight keys (i.e. {Best:1,Actor:2,Drama:5})

         # [Tuple descriptor, key genre, key genre, area, area synonym]
BEST_DRESSED = ['best dressed', 'best dressed', 'best dressed', 'best dressed', 'best dressed']
WORST_DRESSED = ['worst dressed','worst dressed', 'worst dressed', 'worst dressed', 'worst dressed']

LIFETIME_AWARD = ['lifetime','life', 'time']

BEST_DRAMA = ['drama','drama','motion picture','film']
BEST_MUSICAL_COMEDY = ['musical','comedy','motion picture','film']
BEST_ANIMATED = ['animated','animated','feature','film']
BEST_FOREIGN = ['foreign','foreign','language','film']
BEST_DRAMA_TV = ['drama', 'drama','tv','television']
BEST_COMEDY_TV = ['musical','comedy','tv','television']
BEST_MOVIE_TV = ['limited series','limited','series','motion picture','television','tv']


BEST_ACTOR_DRAMA = ['best actor', 'drama','drama', 'motion picture', 'film' ] # Good /w hyphen formatting
BEST_ACTOR_DRAMA_TV = ['best actor', 'drama','drama', 'tv', 'television'] # Good
BEST_ACTRESS_DRAMA = ['best actress', 'drama','drama', 'motion picture', 'film'] #Good but close with Argo
BEST_ACTRESS_DRAMA_TV = ['best actress','drama','drama', 'tv','television'] # Good but no first name mentioned
BEST_ACTOR_MUSICAL_COMEDY = ['best actor', 'musical', 'comedy', 'motion picture', 'film'] # Good but close with Les Miserables
BEST_ACTOR_MUSICAL_COMEDY_TV = ['best actor','musical','comedy', 'tv','television'] # Lost to Girls by 1
BEST_ACTRESS_MUSICAL_COMEDY = ['best actress','musical','comedy', 'motion picture','film'] # Good
BEST_ACTRESS_MUSICAL_COMEDY_TV = ['best actress','musical','comedy', 'tv','television'] # Good but no first name (lost tweets)
BEST_SUPPORTING_ACTOR = ['supporting actor', 'supporting','actor','motion picture', 'film']# Good
BEST_SUPPORTING_ACTRESS = ['supporting actress', 'supporting', 'actress','motion picture', 'film'] # Good
BEST_PERFORMANCE_MINISERIES_ACTOR = ['best performance', 'performance','actor', 'series','miniseries', 'tv', 'television', 'film'] #Good
BEST_PERFORMANCE_MINISERIES_ACTRESS = ['best performance','performance','actress', 'series','miniseries', 'tv', 'television','film']#Good
BEST_SUPPORTING_ACTOR_MINISERIES = ['supporting actor', 'supporting','actor', 'series', 'miniseries','tv', 'television', 'film' ] # Lost. Lewis
BEST_SUPPORTING_ACTRESS_MINISERIES = ['supporting actress', 'supporting','actress','series,' 'miniseries','tv', 'television', 'film'] #All going to other supporting actress
BEST_DIRECTOR = ['best director','director','motion picture','film'] #Good
BEST_SCREENPLAY = ['best screenplay','screenplay', 'motion picture','film'] # Good
BEST_ORIGINAL_SCORE = ['original score','score','compose' 'motion picture','film'] # Good (barely)
BEST_ORIGINAL_SONG = ['original song','song','perform', 'motion picture','film'] # Good

catArray2015 = [Category('Cecil B. DeMille Award', LIFETIME_AWARD, ['George Clooney'],['Don Cheadle', 'Julianna Margulies']),
            Category('Best Motion Picture - Drama', BEST_DRAMA, ['Boyhood', 'Foxcatcher', 'The Imitation Game', 'The Theory of Everything'], ['Meryl Streep']),
            Category('Best Motion Picture - Comedy or Musical', BEST_MUSICAL_COMEDY,['Birdman', 'Into the woods', 'Pride', 'St. Vincent', 'The Grand Budapest Hotel'], ['Robert Downey, Jr.']),
            Category('Best Screenplay - Motion Picture', BEST_SCREENPLAY,['Birdman', 'The Grand Budapest Hotel','Gone Girl', 'Boyhood','The Imitation Game'],['Kristen Wiig','Bill Hader']),
            Category('Best Television Series - Drama',BEST_DRAMA_TV,['The Affair', 'Downton Abbey', 'Game of Thrones', 'The Good Wife', 'House of Cards'], ['Adam Levine','Paul Rudd']),
            Category('Best Television Series - Comedy or Musical',BEST_COMEDY_TV,['Transparent', 'Girls', 'Jane the Virgin', 'Orange is the New Black', 'Silicon Valley'],['Bryan Cranston','Kerry Washington']),
            Category('Best Mini-Series Or Motion Picture Made for Television', BEST_MOVIE_TV,['Fargo', 'The Missing', 'The Normal Heart', 'Olive Kitteridge', 'True Detective'],['Jennifer Lopez','Jeremy Renner']),
            Category('Best Animated Feature Film',BEST_ANIMATED,['How to Train Your Dragon 2', 'Big Hero 6', 'The Book of Life', 'The Boxtrolls', 'The Lego Movie'],['Kevin Hart','Salma Hayek']),
            Category('Best Foreign Language Film',BEST_FOREIGN, ['Leviathan', 'Force Majeure', 'Gett: the Trial of Viviane Amsalem', 'Ida', 'Tangerines'],['Lupita Nyongo','Colin Farrell']),
            Category('Best Dressed', BEST_DRESSED,['none'],['none']),
            Category('Worst Dressed', WORST_DRESSED,['none'],['none']),
            Category('Best Performance by an Actor in a Motion Picture - Drama',BEST_ACTOR_DRAMA,['Eddie Redmayne', 'Steve Carell', 'Benedict Cumberbatch', 'Jake Gyllenhaal', 'David Oyelowo'],['Gwyneth Paltrow']),
            Category('Best Performance by an Actor in a Television Series - Drama',BEST_ACTOR_DRAMA_TV,['Kevin Spacey', 'Clive Owen', 'Liev Schreiber', 'James Spader', 'Dominic West'], ['David Duchovny','Katherine Heigl']),
            Category('Best Performance by an Actress in a Motion Picture - Drama',BEST_ACTRESS_DRAMA, ['Julianne Moore', 'Jennifer Aniston', 'Felicity Jones', 'Rosamund Pike', 'Reese Witherspoon'],['Matthew McConaughey']),
            Category('Best Performance by an Actress in a Television Series - Drama',BEST_ACTRESS_DRAMA_TV, ['Ruth Wilson', 'Claire Danes', 'Viola Davis', 'Julianna Margulies', 'Robin Wright'],['Chris Pratt','Anna Faris']),
            Category('Best Performance by an Actor in a Motion Picture - Comedy or Musical', BEST_ACTOR_MUSICAL_COMEDY,['Michael Keaton', 'Ralph Fiennes', 'Bill Murray', 'Joaquin Phoenix' , 'Christoph Waltz'],['Amy Adams']),
            Category('Best Performance by an Actor in a Television Series - Comedy or Musical', BEST_ACTOR_MUSICAL_COMEDY_TV, ['Jeffrey Tambor', 'Louis C. K.', 'Don Cheadle', 'Ricky Gervais', 'William H. Macy'],['Jane Fonda','Lily Tomlin']),
            Category('Best Performance by an Actress in a Motion Picture - Comedy or Musical', BEST_ACTRESS_MUSICAL_COMEDY,['Amy Adams', 'Emily Blunt', 'Helen Mirren', 'Julianne Moore', 'Quvenzhane Wallis'],['Ricky Gervais']),            
            Category('Best Performance by an Actress in a Television Series - Comedy or Musical', BEST_ACTRESS_MUSICAL_COMEDY_TV, ['Gina Rodriguez', 'Lena Dunham', 'Edie Falco', 'Julia Louis-Dreyfux', 'Taylor Schilling'],['Bryan Cranston','Kerry Washington']),
            Category('Best Performance by an Actor In a Supporting Role in a Motion Picture', BEST_SUPPORTING_ACTOR, ['JK Simmons', 'Robert Duvall', 'Ethan Hawke', 'Edward Norton', 'Mark Ruffalo'],['Jennifer Aniston','Benedict Cumberbatch']),
            Category('Best Performance by an Actress In a Supporting Role in a Motion Picture', BEST_SUPPORTING_ACTRESS, ['Patricia Arquette', 'Jessica Chastain', 'Keira Knightley', 'Emma Stone', 'Meryl Streep'],['Jared Leto']),
            Category('Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television', BEST_PERFORMANCE_MINISERIES_ACTOR,['Billy Bob Thornton', 'Martin Freeman', 'Woody Harrelson', 'Matthew Mcconaughey', 'Mark Ruffalo'],['Jennifer Lopez','Jeremy Renner']),
            Category('Best Performance by an Actress in a Mini-Series or Motion Picture Made for Television', BEST_PERFORMANCE_MINISERIES_ACTRESS,['Maggie Gyllenhaal', 'Jessica Lange', 'Frances Mcdormand', "Frances O'Connor", 'Allison Tolman'],['Adrien Brody','Kate Beckinsale']),
            Category('Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television', BEST_SUPPORTING_ACTOR_MINISERIES,['Matt Bomer', 'Alan Cumming', 'Colin Hanks', 'Bill Murray', 'Jon Voight'],['Seth Meyers', 'Katie Holmes']),
            Category('Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television', BEST_SUPPORTING_ACTRESS_MINISERIES, ['Joanne Froggatt', 'Uzo Aduba', 'Kathy Bates', 'Allison Janney', 'Michelle Monaghan'],['Jamie Dornan','Dakota Johnson']),            
            Category('Best Director - Motion Picture', BEST_DIRECTOR, ['Richard Linklater', 'Wes Anderson', 'Ava Duvernay', 'David Fincher', 'Alejandro Gonzalez Inarritu'],['Harrison Ford']),
            Category('Best Original Score - Motion Picture', BEST_ORIGINAL_SCORE, ['Johann Johannsson', 'Alexandre Desplat', 'Trent Reznor', 'Antonio Sanchez', 'Hans Zimmer'],['Sienna Miller','Vince Vaughn']),
            Category('Best Original Song - Motion Picture', BEST_ORIGINAL_SONG, ['Glory', 'Big Eyes', 'Mercy Is', 'Opportunity', 'Yellow Flicker Beat'],['Prince'])]

catArray2013 = [Category('Cecil B. DeMille Award', LIFETIME_AWARD, ['Jodie Foster'],['Robert Downey, Jr.']),
            Category('Best Motion Picture - Drama', BEST_DRAMA, ['Argo', 'Django Unchained', 'Life of Pi', 'Lincoln', 'Zero Dark Thirty'], ['Julia Roberts']),
            Category('Best Motion Picture - Comedy or Musical', BEST_MUSICAL_COMEDY,['Les Miserables', 'The Best Exotic Marigold Hotel', 'Moonrise Kingdom', 'Salmon Fishing in the Yemen', 'Silver Linings Playbook'], ['Dustin Hoffman']),
            Category('Best Screenplay - Motion Picture', BEST_SCREENPLAY,['Django Unchained', 'Argo','Lincoln', 'Silver Linings Playbook','Zero Dark Thirty'],['Robert Pattinson','Amanda Seyfried']),
            Category('Best Television Series - Drama',BEST_DRAMA_TV,['Homeland', 'Breaking Bad', 'Boardwalk Empire', 'Downton Abbey', 'The Newsroom'], ['Salma Hayek','Paul Rudd']),
            Category('Best Television Series - Comedy or Musical',BEST_COMEDY_TV,['Girls', 'The Big Bang Theory', 'Episodes', 'Modern Family', 'Smash'],['Jimmy Fallon','Jay Leno']),
            Category('Best Mini-Series Or Motion Picture Made for Television', BEST_MOVIE_TV,['Game Change', 'The Girl', 'The Hour', 'Hatfields & McCoys', 'Political Animals'],['Don Cheadle','Eva Longoria']),
            Category('Best Animated Feature Film',BEST_ANIMATED,['Brave', 'Frankenweenie', 'Hotel Transylvania', 'Rise of the Guardians', 'Wreck-It Ralph'],['Sacha Baron Cohen']),
            Category('Best Foreign Language Film',BEST_FOREIGN, ['Amour', 'A Royal Affair', 'The Intouchables', 'Kon-Tiki', 'Rust and Bone'],['Arnold Schwarzenegger','Sylvester Stallone']),
            Category('Best Dressed', BEST_DRESSED,['none'],['none']),
            Category('Worst Dressed', WORST_DRESSED,['none'],['none']),
            Category('Best Performance by an Actor in a Motion Picture - Drama',BEST_ACTOR_DRAMA,['Daniel Day-Lewis', 'Richard Gere', 'John Hawkes', 'Joaquin Phoenix', 'Denzel Washington'],['George Clooney']),
            Category('Best Performance by an Actor in a Television Series - Drama',BEST_ACTOR_DRAMA_TV,['Damian Lewis', 'Steve Buscemi', 'Bryan Cranston', 'Jeff Daniels', 'Jon Hamm'], ['Salma Hayek','Paul Rudd']),
            Category('Best Performance by an Actress in a Motion Picture - Drama',BEST_ACTRESS_DRAMA, ['Jessica Chastain', 'Marion Cotillard', 'Helen Mirren', 'Naomi Watts', 'Rachel Weisz'],['George Clooney']),
            Category('Best Performance by an Actress in a Television Series - Drama',BEST_ACTRESS_DRAMA_TV, ['Claire Danes', 'Connie Britton', 'Glenn Close', 'Michelle Dockery', 'Julianna Marguiles'],['Nathan Fillion','Lea Michele']),
            Category('Best Performance by an Actor in a Motion Picture - Comedy or Musical', BEST_ACTOR_MUSICAL_COMEDY,['Hugh Jackman', 'Jack Black', 'Bradley Cooper', 'Ewan McGregor' , 'Bill Murray'],['Jennifer Garner']),
            Category('Best Performance by an Actor in a Television Series - Comedy or Musical', BEST_ACTOR_MUSICAL_COMEDY_TV, ['Don Cheadle', 'Alec Baldwin', 'Louis C.K.', 'Matt LeBlanc' , 'Jim Parsons'],['Lucy Liu','Debra Messing']),
            Category('Best Performance by an Actress in a Motion Picture - Comedy or Musical', BEST_ACTRESS_MUSICAL_COMEDY,['Jennifer Lawrence', 'Emily Blunt', 'Judi Dench', 'Maggie Smith', 'Meryl Streep'],['Will Ferrell', 'Kristen Wiig']),            
            Category('Best Performance by an Actress in a Television Series - Comedy or Musical', BEST_ACTRESS_MUSICAL_COMEDY_TV, ['Lena Dunham', 'Zooey Deschanel', 'Tina Fey', 'Julia Louis-Dreyfus', 'Amy Poehler'],['Aziz Ansari','Jason Bateman']),
            Category('Best Performance by an Actor In a Supporting Role in a Motion Picture', BEST_SUPPORTING_ACTOR, ['Christoph Waltz', 'Alan Arkin', 'Leonardo DiCaprio', 'Philip Seymour Hoffman', 'Tommy Lee Jones'],['Bradley Cooper','Kate Hudson']),
            Category('Best Performance by an Actress In a Supporting Role in a Motion Picture', BEST_SUPPORTING_ACTRESS, ['Anne Hathaway', 'Amy Adams', 'Sally Field', 'Helen Hunt', 'Nicole Kidman'],['Megan Fox', 'Jonah Hill']),
            Category('Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television', BEST_PERFORMANCE_MINISERIES_ACTOR,['Kevin Costner', 'Benedict Cumberbatch', 'Woody Harrelson', 'Toby Jones', 'Clive Owen'],['Jessica Alba','Kiefer Sutherland']),
            Category('Best Performance by an Actress in a Mini-Series or Motion Picture Made for Television', BEST_PERFORMANCE_MINISERIES_ACTRESS,['Julianne Moore', 'Nicole Kidman', 'Jessica Lange', 'Sienna Miller', 'Sigourney Weaver'],['Don Cheadle','Eva Longoria']),
            Category('Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television', BEST_SUPPORTING_ACTOR_MINISERIES,['Ed Harris', 'Max Greenfeld', 'Danny Huston', 'Mandy Patinkin', 'Eric Stonestreet'],['Kristen Bell', 'John Krasinski']),
            Category('Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television', BEST_SUPPORTING_ACTRESS_MINISERIES, ['Maggie Smith', 'Hayden Panettiere', 'Archie Panjabi', 'Sarah Paulson', 'Sofia Vergara'],['Dennis Quaid','Kerry Washington']),            
            Category('Best Director - Motion Picture', BEST_DIRECTOR, ['Ben Affleck', 'Kathryn Bigelow', 'Ang Lee', 'Steven Spielberg', 'Quentin Tarantino'],['Halle Berry']),
            Category('Best Original Score - Motion Picture', BEST_ORIGINAL_SCORE, ['Mychael Danna', 'Dario Marianelli', 'Alexandre Desplat', 'John Williams', 'Tom Tykwer, Johnny Klimek & Reinhold Heil'],['Jennifer Lopez','Jason Statham']),
            Category('Best Original Song - Motion Picture', BEST_ORIGINAL_SONG, ['Skyfall', 'For You', 'Not Running Anymore', 'Safe & Sound', 'Suddenly'],['Jennifer Lopez', 'Jason Statham'])]
## Regular Expressions
##  Used to find names 
FN_MD_LN = "([A-Z][a-z]*)[\s-]([A-Z][a-z]*)[\s-]([A-Z][a-z]*)"
FN_and_LN = "([A-Z][a-z]*)[\s-]([A-Z][a-z]*)"
FN_or_LN = "([A-Z][a-z]+)"


####  Used to find nominee phrases
##FN_and_LN_NOM = [re.compile("nominees .*" + FN_and_LN), re.compile(FN_and_LN + ".* nominated")]
##FN_or_LN_NOM = [re.compile("nominees.*" + FN_or_LN), re.compile(FN_or_LN + ".* nominated")]
##
####  Used to find winner phrases
##FN_and_LN_WIN = [re.compile("winner.* is " + FN_and_LN), re.compile(FN_and_LN + " won"),re.compile(FN_and_LN + "wins"), re.compile("awarded to " + FN_and_LN)]
##FN_or_LN_WIN = [re.compile("winner.* is " + FN_or_LN), re.compile(FN_or_LN + " won"), re.compile(FN_or_LN + " wins"), re.compile("awarded to " + FN_or_LN)]
## 
####  Used to find presenter phrases
##FN_and_LN_PRE = [re.compile("presented by" + FN_and_LN)]
##FN_or_LN_PRE = [re.compile("presented by " + FN_or_LN)]

##  Used to find nominee phrases

FN_and_LN_NOM = [re.compile("nominees .*" + FN_and_LN), re.compile(FN_and_LN + ".* nominated")]
FN_or_LN_NOM = [re.compile("nominees.*" + FN_or_LN), re.compile(FN_or_LN + ".* nominated")]

##  Used to find winner phrases
FN_and_LN_WIN = [re.compile("winner.* is " + FN_and_LN), re.compile(FN_and_LN + " won"),re.compile(FN_and_LN + "wins"), re.compile("awarded to " + FN_and_LN)]
FN_or_LN_WIN = [re.compile("winner.* is " + FN_or_LN), re.compile(FN_or_LN + " won"), re.compile(FN_or_LN + " wins"), re.compile("awarded to " + FN_or_LN)]
 
##  Used to find presenter phrases
FN_and_LN_PRE = [re.compile("presented by" + FN_and_LN)]
FN_or_LN_PRE = [re.compile("presented by " + FN_or_LN)]

## processTweets
##  Checks tweets line by line
##      - Tags each tweet
##  Iterative debugger. Probably can remove

def processTweets():
    #fname = "filteredtweets15.txt"
    fname = "gg13tweets.txt"

    with open(fname, "r") as ins:
        feed = [] #Line by line
        for line in ins:
            feed.append(line.split())
    count = 0
    #print len(feed)
    for tweet in feed: # Run through each tweet
        tagTweetCat(tweet)        # Run through each category
        #if count % 1000 == 0:
         #   print str(100*(Decimal(count)/Decimal(len(feed)))) + "% of tweets compiled"
        count += 1
        # change 2013 to 2015 to run the 2015 awards
    for cat in catArray2013:
        temp = cat.findWinner()
                 

## tagTweetCat(tweet)
##  Checks categories one at a time
##  Right now this puts the tweet that has the highest score (for debugging purposes)
def tagTweetCat(tweet):
    ind = -1
    scores = {}
    # Place tweet in appropriate categories
    # change 2013 to 2015 to run the 2015 awards
    for cat in catArray2013:
        ind += 1
        scores[ind] = 0
        # Search word by word and compare against keyword set for each category

        # Compare phrases from tweet to key
        for kword in cat.keys:
            if kword in ' '.join(tweet).lower():
                scores[ind] += 1 #Augment category score
    if max(scores.values()) > 1: # Thresholding
        ind = max(scores.iteritems(), key=operator.itemgetter(1))[0]    # Index of highest scoring category
    else:
        ind = -1
        
    if ind > -1:
        catArray2013[ind].addTweet(tweet)                  # Add Tweet
        temp = findPeople(tweet)
        catArray2013[ind].addWinners(temp[1])    # Add People
        catArray2013[ind].addNominees(temp[0])
        catArray2013[ind].addPresenters(temp[2])
## findPeople(tweet, key)
##  returns set of people in the tweet
def findPeople(tweet):
    nominees = list()
    winnners = list()
    presenters = list()

    ## NOMINEES
    FN_and_LN_noms = []
    FN_or_LN_noms = []
    for pattern in FN_and_LN_NOM:
        FN_and_LN_noms += re.findall(pattern, ' '.join(tweet))
    for pattern in FN_or_LN_NOM:
        FN_or_LN_noms +=  re.findall(pattern, ' '.join(tweet))

    #Filter duplicates
    for name_1 in FN_or_LN_noms:
        for name_2 in FN_and_LN_noms:
            if name_1 in name_2:
                if name_1 in FN_or_LN_noms:
                    FN_or_LN_noms.remove(name_1)      

    ## WINNERS
    FN_and_LN_wins = []
    FN_or_LN_wins = []
    
    for pattern in FN_and_LN_WIN:
        FN_and_LN_wins += re.findall(pattern, ' '.join(tweet))
    for pattern in FN_or_LN_WIN:
        FN_or_LN_wins +=  re.findall(pattern, ' '.join(tweet))

    #Filter duplicates
    for name_1 in FN_or_LN_wins:
        for name_2 in FN_and_LN_wins:
            if name_1 in name_2:
                if name_1 in FN_or_LN_wins:
                    FN_or_LN_wins.remove(name_1)
               

    ## PRESENTERS
    FN_and_LN_pres = []
    FN_or_LN_pres = []
    for pattern in FN_and_LN_NOM:
        FN_and_LN_pres += re.findall(pattern, ' '.join(tweet))
    for pattern in FN_or_LN_NOM:
        FN_or_LN_pres +=  re.findall(pattern, ' '.join(tweet))

    #Filter duplicates
    for name_1 in FN_or_LN_pres:
        for name_2 in FN_and_LN_pres:
            if name_1 in name_2:
                if name_1 in FN_or_LN_pres:
                    FN_or_LN_pres.remove(name_1)
                    
                    
    # Return single names then last names
    winners = FN_or_LN_wins + FN_and_LN_wins
    nominees = FN_or_LN_noms + FN_and_LN_noms
    presenters = FN_or_LN_pres + FN_and_LN_pres
        
    return [nominees,winners,presenters]

        
def text_interface_main(results_dict):
    print "Welcome to the Golden Globes 2015!\n"
    print
    print "Type 1 for movies, 2 for TV"

    award_type = raw_input("Please select the type of awards you'd like to see: ")

    if award_type == "1":
      text_interface_movies(results_dict)
        
    elif award_type == "2":
      text_interface_tv(results_dict)
    else:
      print "Invalid input. Please try again"
      text_interface_main(results_dict)

def text_interface_movies(results_dict):
    print "1. Best Motion Picture - Drama"
    print "2. Best Motion Picture - Musical or Comedy"
    print "3. Best Actor in a Motion Picture - Drama"
    print "4. Best Actress in a Motion Picture - Drama"
    print "5. Best Actor in a Motion Picture - Musical or Comedy"
    print "6. Best Actress in a Motion Picture - Musical or Comedy"
    print "7. Best Supporting Actor in a Motion Picture"
    print "8. Best Supporting Actress in a Motion Picture"
    print "9. Best Director"
    print "10. Best Screenplay"
    print "11. Best Original Score"
    print "12. Best Original Song"
    print "13. Best Animated Feature Film"
    print "14. Best Foreign Language Film"
    award_input = raw_input("Please select the award you'd like to see: ")
    if award_input == "1":
        print results_dict['structured']['Best Motion Picture - Drama']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "2":
        print results_dict['structured']['Best Motion Picture - Comedy or Musical']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "3":
        print results_dict['structured']['Best Performance by an Actor in a Motion Picture - Drama']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "4":
        print results_dict['structured']['Best Performance by an Actress in a Motion Picture - Drama']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "5":
        print results_dict['structured']['Best Performance by an Actor in a Motion Picture - Comedy or Musical']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "6":
        print results_dict['structured']['Best Performance by an Actress in a Motion Picture - Comedy or Musical']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "7":
        print results_dict['structured']['Best Performance by an Actor In a Supporting Role in a Motion Picture']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "8":
        print results_dict['structured']['Best Performance by an Actress In a Supporting Role in a Motion Picture']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "9":
        print results_dict['structured']['Best Director - Motion Picture']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "10":
        print results_dict['structured']['Best Screenplay - Motion Picture']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "11":
        print results_dict['structured']['Best Original Score - Motion Picture']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "12":
        print results_dict['structured']['Best Original Song - Motion Picture']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "13":
        print results_dict['structured']['Best Animated Feature Film']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "14":
        print results_dict['structured']['Best Foreign Language Film']['winner']
        text_interface_after_result(results_dict)
    else:
      print "Invalid input. Please try again"
      text_interface_movies(results_dict)

def text_interface_tv(results_dict):
    print "1. Best Drama Series"
    print "2. Best Musical or Comedy Series"
    print "3. Best Actor in a Television Series - Drama"
    print "4. Best Actress in a Television Series - Drama"
    print "5. Best Actor in a Television Series - Musical or Comedy"
    print "6. Best Actress in a Television Series - Musical or Comedy"
    print "7. Best Actor in a Miniseries or Television Film"
    print "8. Best Actress in a Miniseries or Television Film"
    print "9. Best Supporting Actor in a Series, Miniseries or Television Film"
    print "10. Best Supporting Actress in a Series, Miniseries of Television Film"
    print "11. Best Miniseries or Television Film"
    award_input = raw_input("Please select the award you'd like to see: ")
    if award_input == "1":
        print results_dict['structured']['Best Television Series - Drama']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "2":
        print results_dict['structured']['Best Television Series - Comedy or Musical']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "3":
        print results_dict['structured']['Best Performance by an Actor in a Television Series - Drama']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "4":
        print results_dict['structured']['Best Performance by an Actress in a Television Series - Drama']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "5":
        print results_dict['structured']['Best Performance by an Actor in a Television Series - Comedy or Musical']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "6":
        print results_dict['structured']['Best Performance by an Actress in a Television Series - Comedy or Musical']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "7":
        print results_dict['structured']['Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "8":
        print results_dict['structured']['Best Performance by an Actress in a Mini-Series or Motion Picture Made for Television']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "9":
        print results_dict['structured']['Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "10":
        print results_dict['structured']['Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television']['winner']
        text_interface_after_result(results_dict)
    elif award_input == "11":
        print results_dict['structured']['Best Mini-Series Or Motion Picture Made for Television']['winner']
        text_interface_after_result(results_dict)
    else:
      print "Invalid input. Please try again"
      text_interface_tv(results_dict)

def text_interface_after_result(results_dict):
    return_back = raw_input("Would you like to view another award? (y/n): ")
    if return_back == "y":
      text_interface_main(results_dict)
    elif return_back == "n":
      quit()
    else:
      print "Invalid input. Please try again"
      text_interface_after_result(results_dict)

def construct_results_dict():
  allHosts = ['Amy Poehler', 'Tina Fey']
  allWinners = []
  allAwards = []
  allPresenters = []
  allNominees = []

  structured = {}
# change 2013 to 2015 to run the 2015 awards
  for category in catArray2013:
    allWinners.append(category.winner)
    allAwards.append(category.name)
    allPresenters.append(' '.join(category.presenters))
    allNominees.append(' '.join(category.nominee))
    temp = {'nominees':category.nominee,
          'winner':category.winner,
          'presenters':category.presenters}
    structured[category.name] = temp

  metadata = {"year": 2013,
                           "names": {
                               "hosts": {
                                   "method": "hardcoded",
                                   "method_description": ""
                                     },
                                "nominees": {
                                    "method": "hardcoded",
                                    "method_description": ""
                                    },
                                "awards": {
                                    "method": "hardcoded",
                                    "method_description": ""
                                    },
                                "presenters": {
                                    "method": "hardcoded",
                                    "method_description": ""
                                    }
                            },
                            "mappings": {
                                "nominees": {
                                    "method": "hardcoded",
                                    "method_description": ""
                                    },
                                "presenters": {
                                    "method": "hardcoded",
                                    "method_description": ""
                                    }
                            }
              }

  data = {"unstructured": {
                        "hosts":allHosts,
                        "winners":allWinners,
                        "awards":allAwards,
                        "presenters":allPresenters,
                        "nominees":allNominees
                        },
          "structured": structured}

  newdata = {"metadata": {"year": 2013,
                           "names": {
                           "hosts": {
                               "method": "hardcoded",
                               "method_description": ""
                                 },
                            "nominees": {
                                "method": "hardcoded",
                                "method_description": ""
                                },
                            "awards": {
                                "method": "hardcoded",
                                "method_description": ""
                                },
                            "presenters": {
                                "method": "hardcoded",
                                "method_description": ""
                                }
                            },
                        "mappings": {
                            "nominees": {
                                "method": "hardcoded",
                                "method_description": ""
                                },
                            "presenters": {
                                "method": "hardcoded",
                                "method_description": ""
                                }
                            }
                    },
                "data": {
                    "unstructured": {
                        "hosts":allHosts,
                        "winners":allWinners,
                        "awards":allAwards,
                        "presenters":allPresenters,
                        "nominees":allNominees
                    },
                    "structured": structured
                }
            } 
  return newdata


          
def main():
  debug = 1
  processTweets()
  results_dict = construct_results_dict()

  out_file = open('output13.json','w')
  #if sys.argv[1] == "json":
  if debug == 1:
    json.dump(results_dict, out_file)
  
    
  #elif sys.argv[1] == "text":
  else:
    text_interface_main(results_dict)
  out_file.close()


if __name__ == "__main__":
    main()

    

    

