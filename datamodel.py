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
    


