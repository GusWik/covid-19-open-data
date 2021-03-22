# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict
from pandas import DataFrame
from lib.data_source import DataSource
from lib.time import datetime_isoformat
from lib.metadata_utils import country_subregion1s
from lib.utils import table_merge, table_rename


class AustraliaCovidLiveDataSource(DataSource):
    def parse_dataframes(
        self, dataframes: Dict[str, DataFrame], aux: Dict[str, DataFrame], **parse_opts
    ) -> DataFrame:

        data = dataframes[0]

        data["date"] = data.REPORT_DATE.apply(lambda x: datetime_isoformat(x, "%Y-%m-%d"))
        # Add level1 keys
        subregion1s = country_subregion1s(aux["metadata"], "AU")
        data = table_merge(
            [data, subregion1s],
            left_on="CODE", right_on="subregion1_code", how="left")
        # Country-level record has CODE AU
        country_mask = data["CODE"] == "AUS"
        data.loc[country_mask, "key"] = "AU"
        # Only keep country and subregion1 rows
        data = data[data.key != None]
        data = table_rename(
            data,
            {
                'date': 'date',
                'key': 'key',
                'VACC_DOSE_CNT': 'total_vaccine_doses_administered',
                'VACC_DIST_CNT': 'VACC_DIST_CNT',
                'VACC_PEOPLE_CNT': 'VACC_PEOPLE_CNT',
            },
            drop=True)
        # remove rows without vaccination data
        data.dropna(subset=['total_vaccine_doses_administered'], inplace=True)
        return data
