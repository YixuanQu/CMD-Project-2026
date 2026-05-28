import json
import sqlite3
import pandas as pd


# Data Model - Yixuan

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
        self.creation = str(creation)
        self.timespan = str(timespan)
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
        self.title = str(title)
        self.author = author
        self.publicationDate = str(publicationDate)
        self.venue = str(venue)

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


# Base Handlers - Polyxeni
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


class QueryHandler(Handler):
    def getById(self, id):
        pass


#  Bibliographic Entity Upload Handler -Yixuan

class BibliographicEntityUploadHandler(UploadHandler):
    def pushDataToDb(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                js_data = json.load(f)
                
            rows = []
            for item in js_data:
                rows.append({
                    "id": " ".join(item.get("id", [])),
                    "title": item.get("title") or "",
                    "author": "; ".join(item.get("author", [])),
                    "pub_date": item.get("pub_date") or "",
                    "venue": item.get("venue") or "" 
                })
                
            df = pd.DataFrame(rows)
            conn = sqlite3.connect(self.getDbPathOrUrl())
            df.to_sql("BibliographicEntity", conn, if_exists="replace", index=False)
            conn.close()
            return True
        except Exception as e:
            print(f"Upload Error: {e}")
            return False


# Citation Upload Handler - Saya

class CitationUploadHandler(UploadHandler):
    def pushDataToDb(self, path):
        try:
            from rdflib import Graph, URIRef, Literal
            from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
            
            df = pd.read_csv(path)
            my_graph = Graph()
            base_url = "https://comp-data.github.io/res/"
            
            has_citing_entity = URIRef(base_url + "hasCitingEntity")
            has_cited_entity = URIRef(base_url + "hasCitedEntity")
            creation_date = URIRef("https://schema.org/dateCreated")
            timespan = URIRef(base_url + "timespan")
            journal_self_citation = URIRef(base_url + "journalSelfCitation")
            author_self_citation = URIRef(base_url + "authorSelfCitation")
            
            for idx, row in df.iterrows():
                citation_uri = URIRef(base_url + row["oci"])
                citing_url = URIRef(base_url + row["citing"])
                cited_url = URIRef(base_url + row["cited"])
                
                my_graph.add((citation_uri, has_citing_entity, citing_url))
                my_graph.add((citation_uri, has_cited_entity, cited_url))
                my_graph.add((citation_uri, creation_date, Literal(row["creation"])))
                my_graph.add((citation_uri, timespan, Literal(row["timespan"])))
                my_graph.add((citation_uri, journal_self_citation, Literal(row["journal_sc"])))
                my_graph.add((citation_uri, author_self_citation, Literal(row["author_sc"])))
            
            my_store = SPARQLUpdateStore()
            endpoint = self.getDbPathOrUrl()
            my_store.open((endpoint, endpoint))
            for triple in my_graph.triples((None, None, None)):
                my_store.add(triple)
            my_store.close()
            return True
        except Exception as e:
            print(f"Graph Upload Error: {e}")
            return False



# Bibliographic Entity Query Handler - Yixuan

class BibliographicEntityQueryHandler(QueryHandler):
    def getById(self, id):
        try:
            conn = sqlite3.connect(self.getDbPathOrUrl())
            query = "SELECT * FROM BibliographicEntity WHERE id LIKE ?"
            df = pd.read_sql_query(query, conn, params=(f"%{id}%",))
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

    def getAllBibliographicEntities(self):
        try:
            conn = sqlite3.connect(self.getDbPathOrUrl())
            df = pd.read_sql_query("SELECT * FROM BibliographicEntity", conn)
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

    def getBibliographicEntitiesWithTitle(self, title):
        try:
            conn = sqlite3.connect(self.getDbPathOrUrl())
            df = pd.read_sql_query(
                "SELECT * FROM BibliographicEntity WHERE title = ?",
                conn, params=(title,))
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

    def getBibliographicEntitiesWithAuthor(self, author):
        try:
            conn = sqlite3.connect(self.getDbPathOrUrl())
            df = pd.read_sql_query(
                "SELECT * FROM BibliographicEntity WHERE author LIKE ?",
                conn, params=(f"%{author}%",))
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

    def getBibliographicEntitiesWithinPublicationDate(self, start_date, end_date):
        try:
            conn = sqlite3.connect(self.getDbPathOrUrl())
            if start_date and end_date:
                query = "SELECT * FROM BibliographicEntity WHERE pub_date BETWEEN ? AND ?"
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            elif start_date:
                query = "SELECT * FROM BibliographicEntity WHERE pub_date >= ?"
                df = pd.read_sql_query(query, conn, params=(start_date,))
            elif end_date:
                query = "SELECT * FROM BibliographicEntity WHERE pub_date <= ?"
                df = pd.read_sql_query(query, conn, params=(end_date,))
            else:
                df = pd.read_sql_query("SELECT * FROM BibliographicEntity", conn)
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()

    def getBibliographicEntitiesWithVenue(self, venue):
        try:
            conn = sqlite3.connect(self.getDbPathOrUrl())
            df = pd.read_sql_query(
                "SELECT * FROM BibliographicEntity WHERE venue LIKE ?",
                conn, params=(f"%{venue}%",))
            conn.close()
            return df
        except Exception as e:
            return pd.DataFrame()



# Citation Query Handler - Saya

class CitationQueryHandler(QueryHandler):
    def _run_sparql(self, sparql_filter=""):
        try:
            from SPARQLWrapper import SPARQLWrapper, JSON
            sparql = SPARQLWrapper(self.getDbPathOrUrl())
            base_url = "https://comp-data.github.io/res/"
            
            query = f"""
                SELECT ?oci ?citing ?cited ?creation ?timespan ?journal_sc ?author_sc
                WHERE {{
                    ?oci <{base_url}hasCitingEntity> ?citing .
                    ?oci <{base_url}hasCitedEntity> ?cited .
                    ?oci <https://schema.org/dateCreated> ?creation .
                    ?oci <{base_url}timespan> ?timespan .
                    ?oci <{base_url}journalSelfCitation> ?journal_sc .
                    ?oci <{base_url}authorSelfCitation> ?author_sc .
                    {sparql_filter}
                }}
            """
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            
            rows = []
            for r in results["results"]["bindings"]:
                rows.append({
                    "oci": r["oci"]["value"].replace(base_url, ""),
                    "citing": r["citing"]["value"].replace(base_url, ""),
                    "cited": r["cited"]["value"].replace(base_url, ""),
                    "creation": r["creation"]["value"],
                    "timespan": r["timespan"]["value"],
                    "journal_sc": r["journal_sc"]["value"],
                    "author_sc": r["author_sc"]["value"]
                })
            return pd.DataFrame(rows)
        except Exception as e:
            return pd.DataFrame()

    def getById(self, id):
        base_url = "https://comp-data.github.io/res/"
        return self._run_sparql(f'FILTER(STR(?oci) = "{base_url}{id}")')

    def getAllCitations(self):
        return self._run_sparql()

    def getAllAuthorSelfCitations(self):
        return self._run_sparql('FILTER(?author_sc = "yes")')

    def getAllJournalSelfCitations(self):
        return self._run_sparql('FILTER(?journal_sc = "yes")')

    def getCitationsWithinTimespan(self, min_timespan, max_timespan):
        return self._run_sparql(f'FILTER(?timespan >= "{min_timespan}" && ?timespan <= "{max_timespan}")')

    def getCitationsWithinDate(self, start_date, end_date):
        return self._run_sparql(f'FILTER(?creation >= "{start_date}" && ?creation <= "{end_date}")')


# Basic Query Engine - Polyxeni
class BasicQueryEngine(object):
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
        for handler in self.bibliographicEntityQuery:
            df = handler.getById(id)
            if df is not None and not df.empty:
                row = df.iloc[0]
                identifiers = row["id"].split(" ") if row["id"] else []
                authors = row["author"].split("; ") if row["author"] else []
                return BibliographicEntity(identifiers, row["title"], authors, row["pub_date"], row["venue"])
 
        for handler in self.citationQuery:
            df = handler.getById(id)
            if df is not None and not df.empty:
                row = df.iloc[0]
                return self._build_citation_obj(row)
        return None
 
    def _build_citation_obj(self, row, force_cls=None):
        citing_entity = self.getEntityById(row["citing"])
        cited_entity = self.getEntityById(row["cited"])
 
        citing = citing_entity if citing_entity else BibliographicEntity([row["citing"]], "", [], "", "")
        cited = cited_entity if cited_entity else BibliographicEntity([row["cited"]], "", [], "", "")
 
        if force_cls:
            return force_cls([row["oci"]], row["creation"], row["timespan"], citing, cited)
        if str(row.get("author_sc")).lower() == "yes":
            return AuthorSelfCitation([row["oci"]], row["creation"], row["timespan"], citing, cited)
        elif str(row.get("journal_sc")).lower() == "yes":
            return JournalSelfCitation([row["oci"]], row["creation"], row["timespan"], citing, cited)
        return Citation([row["oci"]], row["creation"], row["timespan"], citing, cited)
    
    def getAllCitations(self):
        result = []
        for handler in self.citationQuery:
            df = handler.getAllCitations()
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    result.append(self._build_citation_obj(row))
        return result
 
    def getAllAuthorSelfCitations(self):
        result = []
        for handler in self.citationQuery:
            df = handler.getAllAuthorSelfCitations()
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    result.append(self._build_citation_obj(row, force_cls=AuthorSelfCitation))
        return result
 
    def getAllJournalSelfCitations(self):
        result = []
        for handler in self.citationQuery:
            df = handler.getAllJournalSelfCitations()
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    result.append(self._build_citation_obj(row, force_cls=JournalSelfCitation))
        return result
 
    def getCitationsWithinTimespan(self, min_timespan, max_timespan):
        result = []
        for handler in self.citationQuery:
            df = handler.getCitationsWithinTimespan(min_timespan, max_timespan)
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    result.append(self._build_citation_obj(row))
        return result
 
    def getCitationsWithinDate(self, start_date, end_date):
        result = []
        for handler in self.citationQuery:
            df = handler.getCitationsWithinDate(start_date, end_date)
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    result.append(self._build_citation_obj(row))
        return result
 
    def _convert_bib_df(self, df):
        res = []
        for _, row in df.iterrows():
            identifiers = row["id"].split(" ") if row["id"] else []
            authors = row["author"].split("; ") if row["author"] else []
            res.append(BibliographicEntity(identifiers, row["title"], authors, row["pub_date"], row["venue"]))
        return res
 
    def getAllBibliographicEntities(self):
        result = []
        for handler in self.bibliographicEntityQuery:
            df = handler.getAllBibliographicEntities()
            if df is not None and not df.empty:
                result.extend(self._convert_bib_df(df))
        return result
 
    def getBibliographicEntitiesWithTitle(self, title):
        result = []
        for handler in self.bibliographicEntityQuery:
            df = handler.getBibliographicEntitiesWithTitle(title)
            if df is not None and not df.empty:
                result.extend(self._convert_bib_df(df))
        return result
 
    def getBibliographicEntitiesWithAuthor(self, author):
        result = []
        for handler in self.bibliographicEntityQuery:
            df = handler.getBibliographicEntitiesWithAuthor(author)
            if df is not None and not df.empty:
                result.extend(self._convert_bib_df(df))
        return result
 
    def getBibliographicEntitiesWithinDate(self, start_date, end_date):
        result = []
        for handler in self.bibliographicEntityQuery:
            df = handler.getBibliographicEntitiesWithinPublicationDate(start_date, end_date)
            if df is not None and not df.empty:
                result.extend(self._convert_bib_df(df))
        return result
    
    def getBibliographicEntitiesWithinPublicationDate(self, start_date, end_date):
        result = []
        for handler in self.bibliographicEntityQuery:
            df = handler.getBibliographicEntitiesWithinPublicationDate(start_date, end_date)
            if df is not None and not df.empty:
                result.extend(self._convert_bib_df(df))
        return result
 
    def getBibliographicEntitiesWithVenue(self, venue):
        result = []
        for handler in self.bibliographicEntityQuery:
            df = handler.getBibliographicEntitiesWithVenue(venue)
            if df is not None and not df.empty:
                result.extend(self._convert_bib_df(df))
        return result
 
 
class FullQueryEngine(BasicQueryEngine):
 
    def getAuthorSelfCitationsByName(self, author_name):
        all_scs = self.getAllAuthorSelfCitations()
        filtered = []
        for citation in all_scs:
            combined_authors = [a.lower() for a in (
                citation.getCitingEntity().getAuthors() +
                citation.getCitedEntity().getAuthors()
            )]
            if author_name.lower() in combined_authors:
                filtered.append(citation)
        return filtered
 
    def getJournalSelfCitationsByName(self, journal_name):
        all_scs = self.getAllJournalSelfCitations()
        filtered = []
        for citation in all_scs:
            venues = [
                citation.getCitingEntity().getVenue().lower(),
                citation.getCitedEntity().getVenue().lower()
            ]
            if journal_name.lower() in venues:
                filtered.append(citation)
        return filtered
 
    def getCitationsOfBibEntityByTitleWithinDate(self, title, min_date, max_date):
        bib_entities = self.getBibliographicEntitiesWithTitle(title)
        if not bib_entities:
            return []
        cited_ids = set()
        for entity in bib_entities:
            for entity_id in entity.getIds():
                for single_id in entity_id.split(" "):
                    if single_id.strip():
                        cited_ids.add(single_id.strip())
 
        result = []
        for handler in self.citationQuery:
            df = handler.getCitationsWithinDate(min_date, max_date)
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    if row["cited"] in cited_ids:
                        result.append(self._build_citation_obj(row))
        return result
 
    def getReferencesOfBibEntityByTitleWithinTimespan(self, title, min_timespan, max_timespan):
        bib_entities = self.getBibliographicEntitiesWithTitle(title)
        if not bib_entities:
            return [] 
        citing_ids = set()
        for entity in bib_entities:
            for entity_id in entity.getIds():
                for single_id in entity_id.split(" "):  
                    if single_id.strip():
                        citing_ids.add(single_id.strip())

        result = []
        for handler in self.citationQuery:
            df = handler.getCitationsWithinTimespan(min_timespan, max_timespan)
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    if row["citing"] in citing_ids:
                        result.append(self._build_citation_obj(row))

        return result