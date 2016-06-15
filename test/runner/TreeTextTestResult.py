from unittest import result
from unittest.util import strclass

class TreeTextTestResult(result.TestResult):
    indent = ' ' * 4
    test_class = None

    def __init__(self, stream, descriptions, verbosity):
        super(TreeTextTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.descriptions = descriptions
        self.verbosity = verbosity

    def getDescription(self, test):
        description = test.shortDescription()
        if self.descriptions and description:
            return self.indent + description
        else:
            return self.indent + str(test)

    def getClassDescription(self, test):
        test_class = test.__class__
        description = test.__doc__
        if self.descriptions and description:
            return description.split('\n')[0].strip()
        else:
            return strclass(test_class)

    def startTest(self, test):
        super(TreeTextTestResult, self).startTest(test)
        if self.test_class != test.__class__:
            self.stream.writeln()
            self.test_class = test.__class__
            self.stream.writeln(self.getClassDescription(test))

        self.stream.write(self.getDescription(test))
        self.stream.write(' ... ')
        self.stream.flush()

    def addSuccess(self, test):
        super(TreeTextTestResult, self).addSuccess(test)
        self.stream.writeln("ok")

    def addError(self, test, err):
        super(TreeTextTestResult, self).addError(test, err)
        self.stream.writeln("ERROR")

    def addFailure(self, test, err):
        super(TreeTextTestResult, self).addFailure(test, err)
        self.stream.writeln("FAIL")

    def addSkip(self, test, reason):
        super(TreeTextTestResult, self).addSkip(test, reason)
        self.stream.writeln("skipped {0!r}".format(reason))

    def addExpectedFailure(self, test, err):
        super(TreeTextTestResult, self).addExpectedFailure(test, err)
        self.stream.writeln("expected failure")

    def addUnexpectedSuccess(self, test):
        super(TreeTextTestResult, self).addUnexpectedSuccess(test)
        self.stream.writeln("unexpected success")

    def printErrors(self):
        self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)

