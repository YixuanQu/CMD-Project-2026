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


class FullQueryEngine(BasicQueryEngine):
    def getAuthorSelfCitationsByName(self, author_name):
        result = []
        for handler in self.citationQuery:
            df = handler.getAllAuthorSelfCitations()
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    citing = BibliographicEntity([row["citing"]], "", [], "", "")
                    cited = BibliographicEntity([row["cited"]], "", [], "", "")
                    result.append(AuthorSelfCitation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result

    def getJournalSelfCitationsByName(self, journal_name):
        result = []
        for handler in self.citationQuery:
            df = handler.getAllJournalSelfCitations()
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    citing = BibliographicEntity([row["citing"]], "", [], "", "")
                    cited = BibliographicEntity([row["cited"]], "", [], "", "")
                    result.append(JournalSelfCitation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result

    def getCitationsOfBibEntityByTitleWithinDate(self, title, min_date, max_date):
        result = []
        bib_entities = self.getBibliographicEntitiesWithTitle(title)
        cited_ids = set()
        for entity in bib_entities:
            for id in entity.getIds():
                cited_ids.add(id)
        for handler in self.citationQuery:
            df = handler.getCitationsWithinDate(min_date, max_date)
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    if row["cited"] in cited_ids:
                        citing = BibliographicEntity([row["citing"]], "", [], "", "")
                        cited = BibliographicEntity([row["cited"]], "", [], "", "")
                        result.append(Citation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result

    def getReferencesOfBibEntityByTitleWithinTimespan(self, title, min_timespan, max_timespan):
        result = []
        bib_entities = self.getBibliographicEntitiesWithTitle(title)
        citing_ids = set()
        for entity in bib_entities:
            for id in entity.getIds():
                citing_ids.add(id)
        for handler in self.citationQuery:
            df = handler.getCitationsWithinTimespan(min_timespan, max_timespan)
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    if row["citing"] in citing_ids:
                        citing = BibliographicEntity([row["citing"]], "", [], "", "")
                        cited = BibliographicEntity([row["cited"]], "", [], "", "")
                        result.append(Citation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result

class FullQueryEngine(BasicQueryEngine):
    def getAuthorSelfCitationsByName(self, author_name):
        result = []
        for handler in self.citationQuery:
            df = handler.getAllAuthorSelfCitations()
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    citing = BibliographicEntity([row["citing"]], "", [], "", "")
                    cited = BibliographicEntity([row["cited"]], "", [], "", "")
                    result.append(AuthorSelfCitation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result

    def getJournalSelfCitationsByName(self, journal_name):
        result = []
        for handler in self.citationQuery:
            df = handler.getAllJournalSelfCitations()
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    citing = BibliographicEntity([row["citing"]], "", [], "", "")
                    cited = BibliographicEntity([row["cited"]], "", [], "", "")
                    result.append(JournalSelfCitation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result

    def getCitationsOfBibEntityByTitleWithinDate(self, title, min_date, max_date):
        result = []
        bib_entities = self.getBibliographicEntitiesWithTitle(title)
        cited_ids = set()
        for entity in bib_entities:
            for id in entity.getIds():
                cited_ids.add(id)
        for handler in self.citationQuery:
            df = handler.getCitationsWithinDate(min_date, max_date)
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    if row["cited"] in cited_ids:
                        citing = BibliographicEntity([row["citing"]], "", [], "", "")
                        cited = BibliographicEntity([row["cited"]], "", [], "", "")
                        result.append(Citation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result

    def getReferencesOfBibEntityByTitleWithinTimespan(self, title, min_timespan, max_timespan):
        result = []
        bib_entities = self.getBibliographicEntitiesWithTitle(title)
        citing_ids = set()
        for entity in bib_entities:
            for id in entity.getIds():
                citing_ids.add(id)
        for handler in self.citationQuery:
            df = handler.getCitationsWithinTimespan(min_timespan, max_timespan)
            if df is not None and len(df) > 0:
                for _, row in df.iterrows():
                    if row["citing"] in citing_ids:
                        citing = BibliographicEntity([row["citing"]], "", [], "", "")
                        cited = BibliographicEntity([row["cited"]], "", [], "", "")
                        result.append(Citation([row["oci"]], row["creation"], row["timespan"], citing, cited))
        return result
