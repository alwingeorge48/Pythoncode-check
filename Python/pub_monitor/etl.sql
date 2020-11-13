DROP TEMPORARY TABLE IF EXISTS tmp_exchanges_data;
CREATE Temporary TABLE tmp_exchanges_data LIKE exchanges_data_processed;

INSERT INTO tmp_exchanges_data 
            ( id, company_id, company_name, doc_link, doc_name, domicile, 
              mkey, publication_date, t_publication_date, trgr, ukey, update_date, `year` ) 
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
       mkey, publication_date, t_publication_date, trgr, ukey, update_date, `year` 
FROM  exchanges_data 
WHERE is_processed = false;

UPDATE tmp_exchanges_data 
SET    doc_link = Concat("https://disclosure.edinet-fsa.go.jp/E01EW/download?", 
                                    Unix_timestamp(publication_date), 
"&uji.bean=ee.bean.parent.EECommonSearchBean&uji.verb=W0EZA106CXP001003Action&SESSIONKEY=" 
, Unix_timestamp(update_date), "&s=", doc_link) 
WHERE  mkey = 'XJPEDINET';

UPDATE tmp_exchanges_data 
SET    doc_link = Concat( 
"https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id=", 
    Substring_index(Substring_index(doc_link, ',', 2), 
    ',', -1), 
    "&year=109&mtype=f&") 
WHERE  doc_link LIKE '%javascript:readfile2%';

DROP TEMPORARY TABLE IF EXISTS t1;
CREATE Temporary TABLE t1 LIKE exchanges_data_processed;

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
	         mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, 
       concat(doc_link, "?access_token=83ff96335c2d45a094df02a206a39ff4") `doc_link`, 
       doc_name, domicile, 
       mkey, publication_date, trgr, ukey, update_date, `year`, 
       1                                          `doc_id`, 
       IF(doc_name LIKE '%correct%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%amend%', true, false)   `is_amended`, 
       'en'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://asx.api.markitdigital.com/asx-research/1.0/file%' 
       AND ( doc_name LIKE '%annual%report%' 
              OR doc_name LIKE '%4e%' OR doc_name LIKE '%10-k%');

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )             
SELECT id, company_id, company_name, 
       concat(doc_link, "?access_token=83ff96335c2d45a094df02a206a39ff4") `doc_link`,
       doc_name, domicile, 
       mkey, publication_date, trgr, ukey, update_date, `year`, 
       2                                          `doc_id`, 
       IF(doc_name LIKE '%correct%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%amend%', true, false)   `is_amended`, 
       'en'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://asx.api.markitdigital.com/asx-research/1.0/file%' 
       AND doc_name LIKE '%sustain%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       3     `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://www.bseindia.com/xml-data/corpfiling/AttachLive%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       4                                         `doc_id`, 
       IF(doc_name LIKE '%revis%', true, false)  `is_corrected`, 
       IF(doc_name LIKE '%update%', true, false) `is_amended`, 
       IF(doc_name LIKE '%english%', 'en', 'zh') `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%http://static.cninfo.com.cn/finalpage%' AND
		( doc_name LIKE '%annual%report%' 
         AND doc_name NOT LIKE '%summary%' 
         AND doc_name NOT LIKE '%cancel%' );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )         
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       4                                         `doc_id`, 
       IF(doc_name LIKE '%修订%', true, false)  `is_corrected`, 
       IF(doc_name LIKE '%更新后%', true, false) `is_amended`, 
       IF(doc_name LIKE '%英文%', 'en', 'zh') `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%http://static.cninfo.com.cn/finalpage%' AND
		( doc_name LIKE '%年度%报告%' 
         AND doc_name NOT LIKE '%摘要%' 
         AND doc_name NOT LIKE '%CSR%' 
         AND doc_name NOT LIKE '%已取消%');

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       5                                         `doc_id`, 
       IF(doc_name LIKE "%修订%", true, false) `is_corrected`, 
       false                                     `is_amended`, 
       IF(doc_name LIKE "%英文%", 'en', 'zh')  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%http://static.cninfo.com.cn/finalpage%' 
       AND doc_name LIKE '%CSR%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, Substring_index(doc_link, '+', 1) `doc_link`, 
       doc_name, domicile, mkey, publication_date, trgr, ukey, update_date, `year`, 
       6                                 `doc_id`, 
       false                             `is_corrected`, 
       false                             `is_amended`, 
       'en'                              `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%hkex%' 
       AND doc_link LIKE '%+%csr%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
	  	 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, Substring_index(doc_link, '+', 1) `doc_link`,
	doc_name, domicile, mkey, publication_date, trgr, ukey, update_date, `year`,
	7 `doc_id`,
    false `is_corrected`,
    false `is_amended`,
    'en' `language`
from tmp_exchanges_data 
where doc_link like '%hkex%'
	and doc_link like '%+%ar%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       8                                         `doc_id`, 
       IF(doc_name LIKE '%revis%', true, false)  `is_corrected`, 
       IF(doc_name LIKE '%update%', true, false) `is_amended`, 
       'en'                                      `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://disclosure.bursamalaysia.com%' 
       AND ( ( REPLACE(doc_name, 'PART', '') LIKE BINARY '%AR%' 
               AND doc_name NOT LIKE BINARY '%IAR%' 
               AND doc_name NOT LIKE BINARY '%CG%' ) 
              OR ( doc_name LIKE '%annual%report%' 
                   AND doc_name NOT LIKE '%integrat%' ) );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       9                                         `doc_id`, 
       IF(doc_name LIKE '%revis%', true, false)  `is_corrected`, 
       IF(doc_name LIKE '%update%', true, false) `is_amended`, 
       'en'                                      `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://disclosure.bursamalaysia.com%' 
       AND ( ( doc_name LIKE BINARY '%CG%' 
               AND doc_name NOT LIKE '%integrated%' 
               AND doc_name NOT LIKE '%sustain%' ) 
              OR doc_name LIKE '%governance%' );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       10                                        `doc_id`, 
       IF(doc_name LIKE '%revis%', true, false)  `is_corrected`, 
       IF(doc_name LIKE '%update%', true, false) `is_amended`, 
       'en'                                      `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://disclosure.bursamalaysia.com%' 
       AND ( doc_name LIKE BINARY '%IR%' 
              OR doc_name LIKE BINARY '%IAR%' 
              OR doc_name LIKE '%integrated%' );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       11                                        `doc_id`, 
       IF(doc_name LIKE '%revis%', true, false)  `is_corrected`, 
       IF(doc_name LIKE '%update%', true, false) `is_amended`, 
       'en'                                      `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://disclosure.bursamalaysia.com%' 
       AND ( doc_name LIKE BINARY '%SR%' 
              OR doc_name LIKE '%sustain%' );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       12                                           `doc_id`, 
       IF(doc_name LIKE '%correct%' 
           OR doc_name LIKE '%revis%'
           OR doc_name LIKE '%정정%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%update%', true, false)    `is_amended`, 
       'kr'                                         `language` 
FROM   tmp_exchanges_data 
WHERE  ( doc_link LIKE '%http://dart.fss.or.kr/%' );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
	 	 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       13    `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%http://englishdart.fss.or.kr/%' 
       AND doc_name LIKE '%annual%report%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       14    `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%http://englishdart.fss.or.kr/%' 
       AND doc_name LIKE '%quarter%report%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       15                                           `doc_id`, 
       IF(doc_name LIKE '%修訂本%', true, false) `is_corrected`, 
       false                                        `is_amended`, 
       IF(doc_name LIKE '%英文%', 'en', 'tw')     `language` 
FROM   tmp_exchanges_data
WHERE  doc_link LIKE '%javascript:readfile2%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
	 	 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       16                                         `doc_id`, 
       IF(doc_name LIKE '%correct%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%amend%', true, false)   `is_amended`, 
       'jp'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  ( mkey = 'XJPEDINET' 
         AND doc_link NOT LIKE '%https://www2.tse.or.jp%' ) 
       AND doc_name LIKE '%annual%report%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       17                                         `doc_id`, 
       IF(doc_name LIKE '%correct%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%amend%', true, false)   `is_amended`, 
       'jp'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  ( mkey = 'XJPEDINET' 
         AND doc_link NOT LIKE '%https://www2.tse.or.jp%' ) 
       AND doc_name LIKE '%internal%report%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       18                                         `doc_id`, 
       IF(doc_name LIKE '%correct%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%amend%', true, false)   `is_amended`, 
       'jp'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  ( mkey = 'XJPEDINET' 
         AND doc_link NOT LIKE '%https://www2.tse.or.jp%' ) 
       AND doc_name LIKE '%extra%report%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       19                                         `doc_id`, 
       IF(doc_name LIKE '%correct%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%amend%', true, false)   `is_amended`, 
       'en'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  ( mkey = 'XJPEDINET' 
         AND doc_link LIKE '%https://www2.tse.or.jp%' ) 
       AND doc_name LIKE '%meeting%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       19                                         `doc_id`, 
       IF(doc_name LIKE '%correct%', true, false) `is_corrected`, 
       IF(doc_name LIKE '%amend%', true, false)   `is_amended`, 
       'jp'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  ( mkey = 'XJPEDINET' 
         AND doc_link LIKE '%https://www2.tse.or.jp%' ) 
       AND ( doc_name LIKE '%招集通知%' 
              OR doc_name LIKE '%招集ご通知%' );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       20                                        `doc_id`, 
       false                                     `is_corrected`, 
       IF(doc_name LIKE '%10%k%a%', true, false) `is_amended`, 
       'en'                                      `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%sec%' 
       AND doc_name LIKE '%10-k%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       21                                        `doc_id`, 
       false                                     `is_corrected`, 
       IF(doc_name LIKE '%20%f%a%', true, false) `is_amended`, 
       'en'                                      `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%sec%' 
       AND doc_name LIKE '%20%f%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       22    `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%sec%' 
       AND doc_name LIKE '%prem14a%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       23                                         `doc_id`, 
       false                                      `is_corrected`, 
       IF(doc_name LIKE '%defa14a%', true, false) `is_amended`, 
       'en'                                       `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%sec%' 
       AND ( doc_name LIKE '%def 14a%' 
              OR doc_name LIKE '%defa14a%' );

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       24    `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%sec%' 
       AND doc_name LIKE '%defm14a%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       25    `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%sec%' 
       AND doc_name LIKE '%defc14a%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
       26    `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://links.sgx.com/%' 
       AND ( doc_name LIKE '%annual%report%' 
              OR doc_name LIKE BINARY '%AR%' ) 
       AND doc_name NOT LIKE '%sustain%' 
       AND doc_name NOT LIKE BINARY '%SR%';

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
		 mkey, publication_date, trgr, ukey, update_date, `year`,  
                 doc_id, is_corrected, is_amended, `language` )
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
	   mkey, publication_date, trgr, ukey, update_date, `year`,
	   27 `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en' `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://links.sgx.com/%' 
AND    ( doc_name LIKE '%sustain%' 
       OR doc_name LIKE binary '%SR%');

INSERT INTO t1 ( id, company_id, company_name, doc_link, doc_name, domicile, 
             mkey, publication_date, trgr, ukey, update_date, `year`, 
             doc_id, is_corrected, is_amended, `language`) 
SELECT id, company_id, company_name, doc_link, doc_name, domicile, 
       mkey, publication_date, trgr, ukey, update_date, `year`, 
       28    `doc_id`, 
       false `is_corrected`, 
       false `is_amended`, 
       'en'  `language` 
FROM   tmp_exchanges_data 
WHERE  doc_link LIKE '%https://www.londonstockexchange.com/news-article%' 
       AND doc_name LIKE '%annual%report%'; 

INSERT INTO t1 (id, company_id, company_name, doc_link, doc_name, domicile,
             mkey, publication_date, trgr, ukey, update_date, `year`,
             doc_id, is_corrected, is_amended, `language`)
SELECT id, company_id, company_name, doc_link, doc_name, domicile,
       mkey, publication_date, trgr, ukey, update_date, `year`,
       29    `doc_id`,
       false `is_corrected`,
       false `is_amended`,
       'en'  `language`
FROM   tmp_exchanges_data
WHERE  doc_link LIKE '%https://www.set.or.th/dat/annual%';

INSERT INTO exchanges_data_processed (id, company_id, company_name, doc_link, doc_name, domicile, mkey, publication_date,
                                      trgr, ukey, update_date, `year`, doc_id, is_corrected, is_amended, `language`)
SELECT id, company_id, company_name, doc_link, doc_name, domicile, mkey, publication_date,
       trgr, ukey, update_date, `year`, doc_id, is_corrected, is_amended, `language`
FROM   t1;

SELECT t.id, t.company_id, t.company_name, IFNULL(t1.doc_link, t.doc_link) `doc_link`, t.doc_name, 
       t.domicile, t.mkey, t.publication_date, t.t_publication_date, t.trgr, t.ukey, t.update_date, 
       t.`year`, t1.`language` `doc_lang`, document.short_name `doc_tag`, document.monitor `monitor`
FROM   tmp_exchanges_data AS t 
       LEFT JOIN t1 
              ON t.id = t1.id
       LEFT JOIN document
              ON t1.doc_id = document.id;
