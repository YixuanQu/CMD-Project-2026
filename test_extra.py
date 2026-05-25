import unittest
from os import sep
from pandas import DataFrame
from impl import CitationUploadHandler, BibliographicEntityUploadHandler
from impl import CitationQueryHandler, BibliographicEntityQueryHandler
from impl import FullQueryEngine
from impl import Citation, BibliographicEntity, AuthorSelfCitation, JournalSelfCitation


class TestProjectExtra(unittest.TestCase):

    citation   = "data" + sep + "dh_citations.csv"
    bib_entity = "data" + sep + "dh_metadata.json"
    relational = "." + sep + "relational.db"
    graph      = "http://127.0.0.1:9999/blazegraph/sparql"

    def setUp(self):
        self.cq = CitationQueryHandler()
        self.cq.setDbPathOrUrl(self.graph)

        self.bq = BibliographicEntityQueryHandler()
        self.bq.setDbPathOrUrl(self.relational)

        self.fq = FullQueryEngine()
        self.fq.addCitationHandler(self.cq)
        self.fq.addBibliographicEntityHandler(self.bq)

    # CitationQueryHandler test

    def test_06_getById_citation_real(self):

        df = self.cq.getById("06901234873-061901796324")
        self.assertIsInstance(df, DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["citing"], "omid:br/06901234873")
        self.assertEqual(df.iloc[0]["cited"],  "omid:br/061901796324")

    def test_07_citation_fields(self):
        df = self.cq.getById("06901234873-061901796324")
        self.assertFalse(df.empty)
        row = df.iloc[0]
        self.assertEqual(row["creation"], "2022-01-26")
        self.assertEqual(row["timespan"], "P3Y2M11D")

    def test_08_all_citations_are_no_sc(self):
        df = self.cq.getById("06901234873-06502556055")
        self.assertFalse(df.empty)
        row = df.iloc[0]
        self.assertEqual(row["journal_sc"], "no")
        self.assertEqual(row["author_sc"],  "no")

    def test_09_getCitationsWithinDate_real(self):
        df = self.cq.getCitationsWithinDate("2022-01-01", "2022-12-31")
        self.assertIsInstance(df, DataFrame)
        self.assertGreater(len(df), 0)
        for _, row in df.iterrows():
            self.assertTrue(row["creation"] >= "2022-01-01")
            self.assertTrue(row["creation"] <= "2022-12-31")

    def test_10_getCitationsWithinTimespan_real(self):
        df = self.cq.getCitationsWithinTimespan("P2Y", "P5Y")
        self.assertIsInstance(df, DataFrame)


    # BibliographicEntityQueryHandler test

    def test_11_getById_bib_real(self):
        df = self.bq.getById("doi:10.4230/oasics.ldk.2021.8")
        self.assertIsInstance(df, DataFrame)
        self.assertFalse(df.empty)

    def test_12_getById_bib_omid(self):
        df = self.bq.getById("omid:br/0602485")
        self.assertIsInstance(df, DataFrame)
        self.assertFalse(df.empty)

    def test_13_getById_bib_multiple_ids(self):
        df1 = self.bq.getById("omid:br/060310295")
        df2 = self.bq.getById("doi:10.5281/zenodo.1403229")
        self.assertFalse(df1.empty)
        self.assertFalse(df2.empty)
        
        self.assertEqual(df1.iloc[0]["title"], df2.iloc[0]["title"])

    def test_14_getByAuthor_real(self):
        df = self.bq.getBibliographicEntitiesWithAuthor("Hyvönen")
        self.assertIsInstance(df, DataFrame)
        self.assertFalse(df.empty)
        self.assertTrue(df.iloc[0]["author"].find("Hyvönen") >= 0)

    def test_15_getByAuthor_multiple_authors(self):
        df1 = self.bq.getBibliographicEntitiesWithAuthor("Mühleder")
        df2 = self.bq.getBibliographicEntitiesWithAuthor("Arndt")
        df3 = self.bq.getBibliographicEntitiesWithAuthor("Rämisch")
        self.assertFalse(df1.empty)
        self.assertFalse(df2.empty)
        self.assertFalse(df3.empty)

    def test_16_getByAuthor_not_exist(self):
        df = self.bq.getBibliographicEntitiesWithAuthor("not exist")
        self.assertIsInstance(df, DataFrame)
        self.assertTrue(df.empty)

    def test_17_getById_not_exist(self):
        df = self.bq.getById("doi:10.9999/not_exist")
        self.assertIsInstance(df, DataFrame)
        self.assertTrue(df.empty)

    # FullQueryEngine test

    def test_18_getEntityById_returns_bib(self):
        entity = self.fq.getEntityById("omid:br/060310296")
        self.assertIsInstance(entity, BibliographicEntity)

    def test_19_getEntityById_author_check(self):
        entity = self.fq.getEntityById("doi:10.5281/zenodo.2613454")
        self.assertIsInstance(entity, BibliographicEntity)
        authors = entity.getAuthors()
        self.assertIn("Mühleder, Peter", authors)

    def test_20_getEntityById_not_exist(self):
        entity = self.fq.getEntityById("doi:10.9999/not_exist")
        self.assertIsNone(entity)

    def test_21_getCitationsOfBibEntityByTitleWithinDate_returns_citations(self):
        result = self.fq.getCitationsOfBibEntityByTitleWithinDate(
            "machine learning", "2020", "2023"
        )
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, Citation)

        result = self.fq.getReferencesOfBibEntityByTitleWithinTimespan(
            "library", "P2Y", "P15Y"
        )
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, Citation)

    def test_23_citing_entity_in_citation(self):
        df = self.cq.getById("06901234873-061901796324")
        if not df.empty:
            entity = self.fq.getEntityById("06901234873-061901796324")
            citations = self.fq.getAllCitations()
            if citations:
                c = citations[0]
                self.assertIsInstance(c.getCitingEntity(), BibliographicEntity)
                self.assertIsInstance(c.getCitedEntity(), BibliographicEntity)
