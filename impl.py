# YIXUAN
class IdentifiableEntity(object):
    def __init__(self, identifiers):
        self.id = set()
        for identifier in identifiers:
            self.id.add(identifier)
    
    def getIds(self):
        result = []
        for identifier in self.id:
            result.append(identifier)
        result.sort()
        return result

class Citation(IdentifiableEntity):
    def __init__(self, identifiers, creation, timespan, citingEntity, citedEntity):
        super().__init__(identifiers)
        self.creation = creation
        self.timespan = timespan
        self.citingEntity = citingEntity
        self.citedEntity = citedEntity

    def getCreation(self):
        return self.creation
    
    def getTimespan(self):
        return self.timespan
    
    def getCitingEntity(self):
        return self.citingEntity
    
    def getCitedEntity(self):
        return self.citedEntity

class JournalSelfCitation(Citation):
    pass

class AuthorSelfCitation(Citation):
    pass

class BibliographicEntity(IdentifiableEntity):
    def __init__(self, identifiers, title, author, publicationDate, venue):
        super().__init__(identifiers)
        self.title = title
        self.author = author
        self.publicationDate = publicationDate
        self.venue = venue
    
    def getTitle(self):
        return self.title
    
    def getAuthors(self):
        result = []
        for author in self.author:
            result.append(author)
        result.sort()
        return result
    
    def getPublicationDate(self):
        return self.publicationDate
    
    def getVenue(self):
        return self.venue
    
    

 
# SAYA - add your code here:



# POLYXENI
class Handler(object):
    def __init__(self):
        self.dbPathOrUrl = ""
    
    def getDbPathOrUrl(self):
        return self.dbPathOrUrl
    
    def setDbPathOrUrl(self, pathOrUrl):
        self.dbPathOrUrl = pathOrUrl
        return True

class UploadHandler(Handler):
    def pushDataToDb(self, path):
        pass

class BibliographicEntityUploadHandler(UploadHandler):
    def pushDataToDb(self, path):
        pass

class QueryHandler(Handler):
    def getById(self, id):
        pass

class BibliographicEntityQueryHandler(QueryHandler):
    def getById(self, id):
        pass
    def getAllBibliographicEntities(self):
        pass
    def getBibliographicEntitiesWithTitle(self, title):
        pass
    def getBibliographicEntitiesWithAuthor(self, author):
        pass
    def getBibliographicEntitiesWithinPublicationDate(self, start_date, end_date):
        pass
    def getBibliographicEntitiesWithVenue(self, venue):
        pass


class BasicQueryEngine:
    def __init__(self):
        self.citationQuery = []
        self.bibliographicEntityQuery = []

    def cleanCitationHandlers(self):
        self.citationQuery = []
        return True

    def cleanBibliographicEntityHandlers(self):
        self.bibliographicEntityQuery = []
        return True

    def addCitationHandler(self, handler):
        self.citationQuery.append(handler)
        return True

    def addBibliographicEntityHandler(self, handler):
        self.bibliographicEntityQuery.append(handler)
        return True

    def getEntityById(self, id):
        return None

    def getAllCitations(self):
        return []

    def getAllAuthorSelfCitations(self):
        return []

    def getAllJournalSelfCitations(self):
        return []

    def getCitationsWithinTimespan(self, min_timespan, max_timespan):
        return []

    def getCitationsWithinDate(self, start_date, end_date):
        return []

    def getAllBibliographicEntities(self):
        return []

    def getBibliographicEntitiesWithTitle(self, title):
        return []

    def getBibliographicEntitiesWithAuthor(self, author):
        return []

    def getBibliographicEntitiesWithinPublicationDate(self, start_date, end_date):
        return []

    def getBibliographicEntitiesWithVenue(self, venue):
        return []

class FullQueryEngine(BasicQueryEngine):
    def getAuthorSelfCitationsByName(self, author_name):
        return []

    def getJournalSelfCitationsByName(self, journal_name):
        return []

    def getCitationsOfBibEntityByTitleWithinDate(self, title, min_date, max_date):
        return []

    def getReferencesOfBibEntityByTitleWithinTimespan(self, title, min_timespan, max_timespan):
        return []
