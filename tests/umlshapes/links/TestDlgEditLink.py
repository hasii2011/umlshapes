
from unittest import TestSuite
from unittest import defaultTestLoader
from unittest import main as unitTestMain

from codeallyadvanced.ui.UnitTestBaseW import UnitTestBaseW

from umlmodel.Actor import Actor
from umlmodel.Class import Class
from umlmodel.Link import Link
from umlmodel.UseCase import UseCase
from umlmodel.enumerations.LinkType import LinkType

from umlshapes.dialogs.DlgEditLink import DlgEditLink

CLASS_LINK_NAME:        str = 'owns'
ACTOR_USECASE_NAME:     str = 'initiates'
UPDATED_NAME:           str = 'triggers'
SOURCE_CARDINALITY:     str = '1'
DESTINATION_CARDINALITY: str = '0..*'
NO_CARDINALITY:         str = ''


class TestDlgEditLink(UnitTestBaseW):
    """
    Unit tests for DlgEditLink cardinality control state.
    """

    def testClassToClassLinkEnablesCardinalityControls(self):
        """
        Verify cardinality labels and inputs remain enabled for Class-to-Class associations.
        """
        sourceClass:      Class = Class(name='Order')
        destinationClass: Class = Class(name='LineItem')

        modelLink: Link = Link(name=CLASS_LINK_NAME, linkType=LinkType.ASSOCIATION)
        modelLink.source                 = sourceClass
        modelLink.destination            = destinationClass
        modelLink.sourceCardinality      = SOURCE_CARDINALITY
        modelLink.destinationCardinality = DESTINATION_CARDINALITY

        with DlgEditLink(parent=self._listeningWindow, link=modelLink) as dlg:
            self.assertTrue(dlg._sourceCardinalityLabel.IsEnabled())
            self.assertTrue(dlg._destinationCardinalityLabel.IsEnabled())
            self.assertTrue(dlg._sourceCardinality.IsEnabled())
            self.assertTrue(dlg._destinationCardinality.IsEnabled())
            self.assertTrue(dlg._relationship.IsEnabled())

            dlg._relationship.SetValue(UPDATED_NAME)
            dlg._sourceCardinality.SetValue('1..*')
            dlg._destinationCardinality.SetValue('1')

            updatedLink: Link = dlg.value
            self.assertEqual(UPDATED_NAME, updatedLink.name)
            self.assertEqual('1..*', updatedLink.sourceCardinality)
            self.assertEqual('1', updatedLink.destinationCardinality)

    def testActorToUseCaseLinkDisablesCardinalityControls(self):
        """
        Verify cardinality labels and inputs are disabled for Actor-to-UseCase associations.
        """
        modelActor:   Actor   = Actor(actorName='Customer')
        modelUseCase: UseCase = UseCase(name='Checkout')

        modelLink: Link = Link(name=ACTOR_USECASE_NAME, linkType=LinkType.ASSOCIATION)
        modelLink.source                 = modelActor
        modelLink.destination            = modelUseCase
        modelLink.sourceCardinality      = NO_CARDINALITY
        modelLink.destinationCardinality = NO_CARDINALITY

        with DlgEditLink(parent=self._listeningWindow, link=modelLink) as dlg:
            self.assertFalse(dlg._sourceCardinalityLabel.IsEnabled())
            self.assertFalse(dlg._destinationCardinalityLabel.IsEnabled())
            self.assertFalse(dlg._sourceCardinality.IsEnabled())
            self.assertFalse(dlg._destinationCardinality.IsEnabled())
            self.assertTrue(dlg._relationship.IsEnabled())

            dlg._relationship.SetValue(UPDATED_NAME)

            updatedLink: Link = dlg.value
            self.assertEqual(UPDATED_NAME, updatedLink.name)
            self.assertEqual(NO_CARDINALITY, updatedLink.sourceCardinality)
            self.assertEqual(NO_CARDINALITY, updatedLink.destinationCardinality)


def suite() -> TestSuite:
    testSuite: TestSuite = TestSuite()
    testSuite.addTest(defaultTestLoader.loadTestsFromTestCase(testCaseClass=TestDlgEditLink))
    return testSuite


if __name__ == '__main__':
    unitTestMain()
