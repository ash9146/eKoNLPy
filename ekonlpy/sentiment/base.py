'''
This module contains base classes for dictionaries.
'''

import abc
from ekonlpy.utils import installpath

LEXICON_PATH = '%s/data/lexicon' % installpath


class BaseDict(object):
    '''
    A base class for sentiment analysis. 
    For now, only 'positive' and 'negative' analysis is supported.
    
    Subclasses should implement ``init_dict``, 
    in which ``_posset`` and ``_negset`` are initialized.
    
    ``Polarity`` and ``Subjectivity`` are calculated in the same way of Lydia system.
    See also http://www.cs.sunysb.edu/~skiena/lydia/
    
    The formula for ``Polarity`` is,
    
    .. math::
    
        Polarity= \\frac{N_{pos}-N_{neg}}{N_{pos}+N_{neg}}
    
    The formula for ``Subjectivity`` is,
    
    .. math::
    
        Subjectivity= \\frac{N_{pos}+N_{neg}}{N}
    
    :type tokenizer: obj    
    :param tokenizer: An object which provides interface of ``tokenize``. 
        If it is ``None``, a default tokenizer, which is defined in ``utils``, will be assigned.
    :param kind: An parameter to select a lexicon file for MPKO subclass.

        0: a lexicon file generated using Naive-bayes classifier with 5-gram tokens as features and
            changes of call rates as positive/negative label.

        1: a lexicon file generated by polarity induction and seed propagation method with 5-gram tokens.

    '''

    __metaclass__ = abc.ABCMeta

    TAG_POL = 'Polarity'
    TAG_SUB = 'Subjectivity'
    TAG_POS = 'Positive'
    TAG_NEG = 'Negative'

    EPSILON = 1e-6

    def __init__(self, tokenizer=None, kind=None):
        self._posdict = {}
        self._negdict = {}
        self._poldict = {}
        self.init_dict(kind)
        if tokenizer is None:
            self.init_tokenizer(kind)
        else:
            self._tokenizer = tokenizer

        assert len(self._posdict) > 0 and len(self._negdict) > 0

    def tokenize(self, text):
        '''
        :type text: str
        :returns: list
        '''
        return self._tokenizer.tokenize(text)

    # def ngramize(self, tokens):
    #     '''
    #     :type tokens: list of tokens
    #     :returns: list
    #     '''
    #     return self._tokenizer.ngramize(tokens)

    @abc.abstractmethod
    def init_tokenizer(self, kind):
        pass

    @abc.abstractmethod
    def init_dict(self, kind):
        pass

    def _get_score(self, term, by_count=True):
        '''Get score for a single term.
        - +1 for positive terms.
        - -1 for negative terms.
        - 0 for others. 
        
        :returns: int
        '''
        if by_count:
            if term in self._posdict.keys():
                return self._posdict[term]
            elif term in self._negdict.keys():
                return self._negdict[term]
            else:
                return 0
        else:
            if term in self._poldict.keys():
                return self._poldict[term]
            else:
                return 0

    def get_score(self, terms, by_count=True):
        '''Get score for a list of terms.
        
        :type terms: list
        :param terms: A list of terms to be analyzed.
        :param by_count; if True, use number of occruences of sentiment tokens

        :returns: dict
        '''
        assert isinstance(terms, list) or isinstance(terms, tuple)
        score_li = [self._get_score(t, by_count) for t in terms]
        pos_score_li = [s for s in score_li if s > 0]
        neg_score_li = [s for s in score_li if s < 0]

        s_pos = sum(pos_score_li)
        s_neg = sum(neg_score_li)

        s_pol = (s_pos + s_neg) * 1.0 / (((s_pos - s_neg) if by_count else len(score_li)) + self.EPSILON)
        s_sub = (len(pos_score_li) + len(neg_score_li)) * 1.0 / (len(score_li) + self.EPSILON)

        return {self.TAG_POS: s_pos,
                self.TAG_NEG: s_neg,
                self.TAG_POL: s_pol,
                self.TAG_SUB: s_sub}
