from NIPTool.build.sample import build_sample	
import pytest	


def test_build_sample():	
   # GIVEN a sample_data with requiered key 'SampleID'	
   sample_data = {"SampleID": "2020-07452-02",
                  "SampleType": " ",
                  "Description": " ",
                  "SampleProject": 201862,
                  "Zscore_13": -10.1836097044367}	

   # WHEN building a mongo application tag	
   mongo_application_tag = build_sample(sample_data = sample_data)	

   # THEN assert mongo_application_tag is 
   # {"_id": "2020-07452-02","SampleID": "2020-07452-02",
   # "SampleProject": "201862","Zscore_13": -10.1836097044367} 

   assert mongo_application_tag ==  {"_id": "2020-07452-02", 
                                     "SampleID": "2020-07452-02",
                                     "SampleProject": "201862",
                                     "Zscore_13": -10.1836097044367}

