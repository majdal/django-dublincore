import os
from collections import defaultdict
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from dublincore.models import  QualifiedDublinCoreElement

class QDCElementTestCase(TestCase):
    fixtures = ['DublinCore.qualifieddublincoreelementTest.json', 'DublinCore.auth.json']

    def testQDC(self):
        dc = QualifiedDublinCoreElement.objects.get(pk=1)
        self.assertEqual(dc.qdc, '<title>Court House,Eureka, Cal</title>')

    def testQDCE_extended_term_save(self):
        '''Test the saving of an extended term from the DCTERMS'''
        q=QualifiedDublinCoreElement()
        q.term = 'RH'
        q.content = 'XXXXX  TEXT XXXXX'
        q.object_id = 9
        q.content_type = ContentType.objects.get(app_label='auth', model='user')
        self.assertRaises(ValueError, q.save)
        q.term = 'T'
        q.save()

class DCTermOACOrderingTestCase(TestCase):
    '''Test that any DC term list has the same order as OAC. Also verify that 
    all of the terms are next to one another (subject all grouped, etc.)
    '''
    fixtures = ['DublinCore.qualifieddublincoreelementTest.json', 'DublinCore.auth.json']

    def setUp(self):
        super(DCTermOACOrderingTestCase, self).setUp()
        os.environ['XTF_DATA'] = os.path.abspath(os.path.join(os.path.dirname(__file__), "data/xtf/data/"))

    def testTermsGrouped(self):
        ''' Test that the DC for an object is grouped by the term type
        ie all subject terms come in a row, all titles, etc.
        '''
        qdc = QualifiedDublinCoreElement()
        qdc.term = 'SUB'
        qdc.content = 'TEST'
        dcterms = QualifiedDublinCoreElement.objects.all()
        seen = defaultdict(int)
        curterm = dcterms[0].term
        for qdct in dcterms:
            if curterm != qdct.term:
                #switched or revisited
                if seen[qdct.term] == 1:
                    self.fail('Out of order term:%s' % qdct)
            curterm = qdct.term
            seen[qdct.term] = 1

class QDublinCoreElementHistoryTestCase(TestCase):
    ''' Test the saving of previous values for QualifiedDublinCoreElement objects
    '''
    fixtures = ['DublinCore.qualifieddublincoreelementTest.json', 'DublinCore.auth.json']

    def setUp(self):
        super(QDublinCoreElementHistoryTestCase, self).setUp()
        os.environ['XTF_DATA'] = os.path.abspath(os.path.join(os.path.dirname(__file__), "data/xtf/data/"))

    def testQDublinCoreElementNewHistory(self):
        '''Create a QualifiedDublinCoreElement, save it. No history yet.
        '''
        dct = QualifiedDublinCoreElement()
        dct.content_object = User.objects.get(pk=1)
        dct.term = 'T'
        dct.content = 'X'
        dct.save()
        self.failUnless(len(dct.history.all()) == 0)
        dct.content = 'Y'
        dct.save()
        self.failUnless(len(dct.history.all()) == 1)

    def testQDublinCoreElementHistorySave(self):
        '''Get an existing QualifiedDublinCoreElement. No history yet.
        Then change and save it. Should have history now.
        '''
        dct = QualifiedDublinCoreElement.objects.get(pk=1)
        self.failUnless(len(dct.history.all()) == 0)
        dct.save()
        self.failUnless(len(dct.history.all()) == 0)
        dct.content = 'XXXXX'
        dct.save()
        self.failUnless(len(dct.history.all()) == 1)
        dct.content = 'YYYY'
        dct.save()
        self.failUnless(len(dct.history.all()) == 2)
        dct.content = 'YYYY'
        dct.save()
        self.failUnless(len(dct.history.all()) == 2)
        dct.content = 'ZZZZ'
        dct.save()
        self.failUnless(len(dct.history.all()) == 3)
        dct.qualifier = 'ZZZZ'
        dct.save()
        self.failUnless(len(dct.history.all()) == 4)
        dct.term = 'REL'
        self.assertRaises(ValueError, dct.save)
