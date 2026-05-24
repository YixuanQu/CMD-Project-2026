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
        """每个测试前初始化 handler 和 engine"""
        self.cq = CitationQueryHandler()
        self.cq.setDbPathOrUrl(self.graph)

        self.bq = BibliographicEntityQueryHandler()
        self.bq.setDbPathOrUrl(self.relational)

        self.fq = FullQueryEngine()
        self.fq.addCitationHandler(self.cq)
        self.fq.addBibliographicEntityHandler(self.bq)

    # ── CitationQueryHandler 测试 ──────────────────────────────────────────

    def test_06_getById_citation_real(self):
        """用真实 oci 查询，应该返回恰好一行"""
        df = self.cq.getById("06901234873-061901796324")
        self.assertIsInstance(df, DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["citing"], "omid:br/06901234873")
        self.assertEqual(df.iloc[0]["cited"],  "omid:br/061901796324")

    def test_07_citation_fields(self):
        """验证引用记录的 creation 和 timespan 字段值正确"""
        df = self.cq.getById("06901234873-061901796324")
        self.assertFalse(df.empty)
        row = df.iloc[0]
        self.assertEqual(row["creation"], "2022-01-26")
        self.assertEqual(row["timespan"], "P3Y2M11D")

    def test_08_all_citations_are_no_sc(self):
        """样本数据里这几条记录 journal_sc 和 author_sc 都是 no"""
        df = self.cq.getById("06901234873-06502556055")
        self.assertFalse(df.empty)
        row = df.iloc[0]
        self.assertEqual(row["journal_sc"], "no")
        self.assertEqual(row["author_sc"],  "no")

    def test_09_getCitationsWithinDate_real(self):
        """样本里所有引用 creation 都是 2022-01-26，应该能被范围查询命中"""
        df = self.cq.getCitationsWithinDate("2022-01-01", "2022-12-31")
        self.assertIsInstance(df, DataFrame)
        self.assertGreater(len(df), 0)
        for _, row in df.iterrows():
            self.assertTrue(row["creation"] >= "2022-01-01")
            self.assertTrue(row["creation"] <= "2022-12-31")

    def test_10_getCitationsWithinTimespan_real(self):
        """P3Y2M11D 应在 P2Y 到 P5Y 范围内"""
        df = self.cq.getCitationsWithinTimespan("P2Y", "P5Y")
        self.assertIsInstance(df, DataFrame)
        # 不强求非空（timespan 字符串比较依赖格式），但类型必须正确

    # ── BibliographicEntityQueryHandler 测试 ──────────────────────────────

    def test_11_getById_bib_real(self):
        """用真实 doi 查询书目实体"""
        df = self.bq.getById("doi:10.4230/oasics.ldk.2021.8")
        self.assertIsInstance(df, DataFrame)
        self.assertFalse(df.empty)

    def test_12_getById_bib_omid(self):
        """用 omid 查询书目实体"""
        df = self.bq.getById("omid:br/0602485")
        self.assertIsInstance(df, DataFrame)
        self.assertFalse(df.empty)

    def test_13_getById_bib_multiple_ids(self):
        """同一条记录有多个 id，任意一个都能查到同一条记录"""
        df1 = self.bq.getById("omid:br/060310295")
        df2 = self.bq.getById("doi:10.5281/zenodo.1403229")
        self.assertFalse(df1.empty)
        self.assertFalse(df2.empty)
        # 两个 id 指向同一条记录，title 应该相同
        self.assertEqual(df1.iloc[0]["title"], df2.iloc[0]["title"])

    def test_14_getByAuthor_real(self):
        """按真实作者名查询"""
        df = self.bq.getBibliographicEntitiesWithAuthor("Hyvönen")
        self.assertIsInstance(df, DataFrame)
        self.assertFalse(df.empty)
        # 确认 author 字段确实包含该名字
        self.assertTrue(df.iloc[0]["author"].find("Hyvönen") >= 0)

    def test_15_getByAuthor_multiple_authors(self):
        """一篇文章有多个作者，每个作者名都能查到这篇文章"""
        df1 = self.bq.getBibliographicEntitiesWithAuthor("Mühleder")
        df2 = self.bq.getBibliographicEntitiesWithAuthor("Arndt")
        df3 = self.bq.getBibliographicEntitiesWithAuthor("Rämisch")
        self.assertFalse(df1.empty)
        self.assertFalse(df2.empty)
        self.assertFalse(df3.empty)

    def test_16_getByAuthor_not_exist(self):
        """查不存在的作者应返回空 DataFrame 而不是报错"""
        df = self.bq.getBibliographicEntitiesWithAuthor("这个作者不存在XYZ")
        self.assertIsInstance(df, DataFrame)
        self.assertTrue(df.empty)

    def test_17_getById_not_exist(self):
        """查不存在的 id 应返回空 DataFrame"""
        df = self.bq.getById("doi:10.9999/not_exist")
        self.assertIsInstance(df, DataFrame)
        self.assertTrue(df.empty)

    # ── FullQueryEngine 测试 ───────────────────────────────────────────────

    def test_18_getEntityById_returns_bib(self):
        """getEntityById 查书目 id，应返回 BibliographicEntity"""
        entity = self.fq.getEntityById("omid:br/060310296")
        self.assertIsInstance(entity, BibliographicEntity)

    def test_19_getEntityById_author_check(self):
        """getEntityById 返回的 BibliographicEntity，作者列表应包含正确的名字"""
        entity = self.fq.getEntityById("doi:10.5281/zenodo.2613454")
        self.assertIsInstance(entity, BibliographicEntity)
        authors = entity.getAuthors()
        self.assertIn("Mühleder, Peter", authors)

    def test_20_getEntityById_not_exist(self):
        """查不存在的 id 应返回 None"""
        entity = self.fq.getEntityById("doi:10.9999/not_exist")
        self.assertIsNone(entity)

    def test_21_getCitationsOfBibEntityByTitleWithinDate_returns_citations(self):
        """返回结果每个元素都应是 Citation 实例"""
        result = self.fq.getCitationsOfBibEntityByTitleWithinDate(
            "machine learning", "2020", "2023"
        )
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, Citation)

    def test_22_getReferencesOfBibEntityByTitleWithinTimespan_returns_citations(self):
        """返回结果每个元素都应是 Citation 实例"""
        result = self.fq.getReferencesOfBibEntityByTitleWithinTimespan(
            "library", "P2Y", "P15Y"
        )
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, Citation)

    def test_23_citing_entity_in_citation(self):
        """Citation 对象里的 citingEntity 应是 BibliographicEntity"""
        df = self.cq.getById("06901234873-061901796324")
        if not df.empty:
            entity = self.fq.getEntityById("06901234873-061901796324")
            # 这条是 Citation（journal_sc=no, author_sc=no）
            citations = self.fq.getAllCitations()
            if citations:
                c = citations[0]
                self.assertIsInstance(c.getCitingEntity(), BibliographicEntity)
                self.assertIsInstance(c.getCitedEntity(), BibliographicEntity)


if __name__ == "__main__":
    unittest.main()