import re
import warnings

import logging

import nltk
import numpy as np
import pandas as pd
from nltk import ngrams
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from textblob import Word

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

warnings.filterwarnings("ignore")

SYNONYM_LIMIT = 0


logger = logging.getLogger(__name__)


class SearchKeywordGenerator:
    def __init__(
        self, headings_file, ga_search_terms_file, trade_tariff_synonyms, output_file
    ):

        self.stop_words = set(stopwords.words("english"))
        self.subhead = pd.read_csv(headings_file)
        self.google_analytics_searched_words = pd.read_excel(
            ga_search_terms_file, sheetname="Dataset1"
        )
        self.trade_tariff_synonyms = trade_tariff_synonyms
        self.output_file = output_file

        self.searched_words = self.get_searched_words()
        self.searched_pair_words = self.get_searched_pair_words()

    def get_searched_words(self):
        """
        convert GA searched items to singular words
        :return: list
        """
        words = self.google_analytics_searched_words["Search Term"]
        return [Word(word).singularize() for word in words if word is not np.nan]

    def get_searched_pair_words(self):
        """
        define searched pair words
        :return: list
        """
        words = [word for word in self.searched_words if " " in word]
        return [Word(word).singularize() for word in words]

    def filter_stop_words(self, content, stop_words):
        """
        define filter_stop_words function to remove stop words
        :param content: the content searched
        :param stop_words: the stop words
        :return: list converted to string
        """
        content = re.sub(r"[^\w\s]", "", content)
        content = re.sub(r"[0-9]+", "", content)
        new_sent = [
            Word(word).singularize()
            for word in content.lower().split()
            if Word(word).singularize() not in stop_words
        ]
        new_cont = " ".join(new_sent)
        return new_cont

    def get_searched_single_word(self, content, stop_words):
        """
        define searched_singleword_func to return single words, which have been searched, from content
        :param content: the content searched
        :param stop_words: the stop words
        :return: list converted to string
        """
        content = re.sub(r"[^\w\s]", "", content)
        content = re.sub(r"[0-9]+", "", content)
        new_sent = [
            Word(word).singularize()
            for word in content.lower().split()
            if Word(word).singularize() not in stop_words
        ]
        new_sent = [
            Word(word).singularize()
            for word in new_sent
            if Word(word).singularize() in set(self.searched_words)
        ]
        new_cont = " ".join(new_sent)
        return new_cont

    def get_searched_unique_single_word(self, content, stop_words):
        """
        define searched_unique_singleword to return unique singleword which have been searched from content
        :param content: the content searched
        :param stop_words: the stop words
        :return: list converted to string
        """
        content = re.sub(r"[^\w\s]", "", content)
        content = re.sub(r"[0-9]+", "", content)
        new_sent = [
            Word(word).singularize()
            for word in content.lower().split()
            if Word(word).singularize() not in stop_words
        ]
        new_sent = [
            Word(word).singularize()
            for word in new_sent
            if Word(word).singularize() in set(self.searched_words)
        ]
        uni_cont = []
        for w in new_sent:
            if w not in uni_cont:
                uni_cont.append(w)
        uni_cont = " ".join(uni_cont)
        return uni_cont

    def get_un_searched_single_word(self, content, stop_words):
        """
        define unsearched_singlewords to return single words which have not been searched from content
        :param content: the content searched
        :param stop_words: the stop words
        :return: list converted to string
        """
        content = re.sub(r"[^\w\s]", "", content)
        content = re.sub(r"[0-9]+", "", content)
        new_sent = [
            Word(word).singularize()
            for word in content.lower().split()
            if Word(word).singularize() not in stop_words
        ]
        new_sent = [
            Word(word).singularize()
            for word in new_sent
            if Word(word).singularize() not in set(self.searched_words)
        ]
        new_cont = " ".join(new_sent)
        return new_cont

    def get_searched_paired_word(self, content, stop_words):
        """
        define searched_pairwords to return searched pair words from content
        :param content: the content searched
        :param stop_words: the stop words
        :return: list converted to string
        """
        content = re.sub(r"[^\w\s]", "", content)
        content = re.sub(r"[0-9]+", "", content)
        content = [
            Word(word).singularize()
            for word in content.lower().split()
            if Word(word).singularize() not in stop_words
        ]
        content = " ".join(content)

        # extract pair words
        pair_gram = ngrams(content.split(), 2)
        pairword = [" ".join(element) for element in pair_gram]
        searched_pair_word = [
            p_word for p_word in pairword if p_word in self.searched_pair_words
        ]
        searched_pair_word = list(
            dict.fromkeys(searched_pair_word)
        )  # return unique pairword in the list
        searched_pair_word = " ".join(searched_pair_word)
        return searched_pair_word

    def get_searched_single_word_synonym(self, content, stop_words):
        """
        define searched_singleword_synonym to return single words's synonym, which have been searched, from content
        :param content: the content searched
        :param stop_words: the stop words
        :return: unique synonyms as list converted to string
        """
        content = re.sub(r"[^\w\s]", "", content)
        content = re.sub(r"[0-9]+", "", content)
        new_sent = [
            Word(word).singularize()
            for word in content.lower().split()
            if Word(word).singularize() not in stop_words
        ]
        new_sent = [
            Word(word).singularize()
            for word in new_sent
            if Word(word).singularize() in set(self.searched_words)
        ]

        syn = []
        for w in new_sent:
            for s in wordnet.synsets(w):
                for lemma in s.lemmas():
                    if len(syn) == SYNONYM_LIMIT:
                        break
                    syn.append(lemma.name())
        syn = list(dict.fromkeys(syn))  #
        syn = " ".join(syn)
        return syn

    def create_clean_content(self):
        """
        create clean_content, searched_unique_singleword, unsearched_unique_singleword and searched_pairword columns
        """
        clean_content = []
        searched_unique_single_word = []
        un_searched_unique_single_word = []
        searched_pair_word = []
        searched_unique_single_word_synonym = []

        for i in range(self.subhead.shape[0]):
            clean_content.append(
                self.filter_stop_words(self.subhead.Col7[i], self.stop_words)
            )
            searched_unique_single_word.append(
                self.get_searched_unique_single_word(
                    self.subhead.Col7[i], self.stop_words
                )
            )
            un_searched_unique_single_word.append(
                self.get_un_searched_single_word(self.subhead.Col7[i], self.stop_words)
            )
            searched_pair_word.append(
                self.get_searched_paired_word(self.subhead.Col7[i], self.stop_words)
            )
            searched_unique_single_word_synonym.append(
                self.get_searched_single_word_synonym(
                    self.subhead.Col7[i], self.stop_words
                )
            )

        self.subhead["clean_content"] = clean_content
        self.subhead["searched_unique_single_word"] = searched_unique_single_word
        self.subhead["un_searched_unique_single_word"] = un_searched_unique_single_word
        self.subhead["searched_pair_word"] = searched_pair_word
        self.subhead[
            "searched_unique_single_word_synonym"
        ] = searched_unique_single_word_synonym

    @staticmethod
    def change_code(code):
        """
        function to add '0' at the beginning of the code, if it's less than 10 digits
        :param code: commodity_code
        :return: padded commodity code
        """
        if len(str(code)) == 9:
            code = str(0) + str(code)
        else:
            code = str(code)
        return code

    def process(self):
        self.create_clean_content()

        logger.info("Setting subhead searched words..")
        self.set_subhead_searched_words()

        self.set_subhead_final_category()

        logger.info("Setting ranking..")
        self.set_subhead_ranking()

        self.subhead["New_Code"] = self.subhead.Code.apply(self.change_code)

        # get first 4 digits of the Code
        self.subhead["Code_First4Digits"] = self.get_four_digit_code()

        logger.info("Processing synonyms from the Trade Tariff API")
        synonym_data_frame = pd.DataFrame(
            self.trade_tariff_synonyms, columns=["Code_First4Digits", "Contents"]
        )

        self.subhead = self.subhead.merge(
            synonym_data_frame, on="Code_First4Digits", how="left"
        )

        self.subhead.Contents = self.subhead.Contents.replace(np.nan, "", regex=True)
        self.subhead["final_category"] = self.subhead[
            ["final_category", "Contents"]
        ].apply(lambda x: " ".join(x), axis=1)
        self.subhead = self.subhead.drop(
            ["New_Code", "Code_First4Digits", "Contents"], axis=1
        )
        self.subhead["final_category"] = self.subhead["final_category"].str.lower()

        logger.info("Saving output to CSV..")
        self.subhead.to_csv(self.output_file, index=False)
        logger.info("Done!")

    def get_four_digit_code(self):
        """
        get the first four digits of the commodity code
        :return: four digit commodity code
        """
        return (
            self.subhead["New_Code"].str[0:2] + "." + self.subhead["New_Code"].str[2:4]
        )

    def set_subhead_final_category(self):
        """
        create final_category column, if searched_words is empty, we will assign unsearched_unique_singleword to
        final_category, otherwise, use searched_words
        """

        final_category_temp = []
        for i in range(self.subhead.shape[0]):
            if self.subhead["searched_words"][i] == "":
                final_category_temp.append(
                    self.subhead["un_searched_unique_single_word"][i]
                )
            else:
                final_category_temp.append(self.subhead["searched_words"][i])

        # if final_category_temp is still empty, 'other' will be assigned to it
        final_category = []
        for i in range(self.subhead.shape[0]):
            if final_category_temp[i] == "":
                final_category.append("other")
            else:
                final_category.append(final_category_temp[i])
        self.subhead["final_category"] = final_category

    def set_subhead_ranking(self):
        """
        assign a ranking score to final_category based on the hierarchy, higher score for higher hierarchy and
        lower score for lower hierarchy, maximum score is subhead['Col8'].max()
        """
        # remove dirty rows
        # TODO: determine why the "Col8" values appear in rows in the first place
        self.subhead = self.subhead[self.subhead.Col8 != "Col8"]
        # cast all to int so that we can take `.max`
        self.subhead["Col8"] = self.subhead["Col8"].astype("int32")

        self.subhead["ranking_score"] = (
            self.subhead["Col8"].max() - self.subhead["Col8"]
        )

    def set_subhead_searched_words(self):
        """
        combine searched single word's synonym and searched pairword, if searched pairword not in
        searched single word, then append pair word to single word's synonym, otherwise, nothing to do
        """

        searched_words = []
        for i in range(self.subhead.shape[0]):
            if (
                self.subhead["searched_pair_word"][i]
                in self.subhead["searched_unique_single_word_synonym"][i]
            ):
                searched_words.append(
                    self.subhead["searched_unique_single_word_synonym"][i]
                )
            else:
                searched_words.append(
                    self.subhead["searched_unique_single_word_synonym"][i]
                    + self.subhead["searched_pair_word"][i]
                )
        self.subhead["searched_words"] = searched_words
