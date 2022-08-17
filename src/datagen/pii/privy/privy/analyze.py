# Copyright 2018- The Pixie Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
from collections import Counter
import logging


class DatasetAnalyzer:
    def __init__(self, providers):
        # initialize counter of PII types/categories in the generated dataset
        # initialize all categories and pii type counts to 0
        self.count_categories = Counter(
            {k: 0 for k in providers.get_pii_categories()})
        self.count_pii_types = Counter(
            {k: 0 for k in providers.get_pii_types()})
        self.num_payloads = 0
        self.num_pii_payloads = 0
        self.num_payloads_this_spec = 0
        self.num_pii_payloads_this_spec = 0
        self.percent_pii = 0
        self.num_pii_types_per_pii_payload = 0
        self.log = logging.getLogger("privy")

    def get_lowest_count_category(self):
        """Get category with lowest count in the generated dataset"""
        return min(self.count_categories.items(), key=lambda x: x[1])

    def get_lowest_count_pii_type(self):
        """Get pii type with lowest count in the generated dataset"""
        return min(self.count_pii_types.items(), key=lambda x: x[1])

    def k_lowest_pii_types(self, k):
        """Get k pii types with lowest count in the generated dataset"""
        return self.count_pii_types.most_common()[:-k - 1:-1]

    def update_pii_counters(self, pii_types, categories):
        self.count_pii_types.update(pii_types)
        self.count_categories.update(categories)
        self.num_pii_payloads += 1
        self.num_pii_payloads_this_spec += 1

    def reset_spec_specific_metrics(self):
        self.num_payloads_this_spec = 0
        self.num_pii_payloads_this_spec = 0

    def update_payload_counts(self):
        self.num_payloads += 1
        self.num_payloads_this_spec += 1
        if self.num_pii_payloads > 0:
            self.percent_pii = (self.num_pii_payloads / self.num_payloads) * 100
            num_pii_types = sum(self.count_pii_types.values())
            self.num_pii_types_per_pii_payload = num_pii_types / self.num_pii_payloads

    def print_metrics(self):
        self.log.info(
            f"Dataset has these category counts: {self.count_categories}")
        self.log.info(
            f"Dataset has these pii_type counts: {self.count_pii_types}")
        self.log.info(
            f"{self.num_pii_payloads_this_spec} out of {self.num_payloads_this_spec} \
            generated payloads contain PII for this api spec")
        self.log.info(
            f"{self.percent_pii:.2f}% of payloads contain PII")
        self.log.info(
            f"Each PII payload has {self.num_pii_types_per_pii_payload:.2f} \
                PII types on average")
