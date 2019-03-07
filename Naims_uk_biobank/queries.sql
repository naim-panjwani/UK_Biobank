#CREATE DATABASE uk_biobank;

SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA='uk_biobank';

#DROP TABLE `uk_biobank`.`3063_irnt.gwas.imputed_v3.both_sexes.tsv.bgz`;

SELECT *, substring_index(SUBSTRING_INDEX(`variant`, ':', 1), ":", -1) as chr,
substring_index(SUBSTRING_INDEX(`variant`, ':', 2), ":", -1) as pos
FROM `uk_biobank`.`3062_irnt.gwas.imputed_v3.both_sexes.tsv.bgz`
WHERE low_confidence_variant = 0
ORDER BY pval
limit 100;

SELECT * FROM `uk_biobank`.`3062_irnt.gwas.imputed_v3.both_sexes.tsv.bgz`
ORDER BY chr, bp asc
limit 100;

USE `uk_biobank`;
RENAME TABLE `3062_irnt.gwas.imputed_v3.both_sexes.tsv.bgz` TO `3062_irnt_both_sexes`;
RENAME TABLE `3062_raw.gwas.imputed_v3.both_sexes.tsv.bgz` TO `3062_raw_both_sexes`;

ALTER TABLE `3062_irnt_both_sexes`
CHANGE COLUMN bp pos int;
ALTER TABLE `uk_biobank`.`3062_raw_both_sexes`
CHANGE COLUMN bp pos int;


SELECT * FROM `uk_biobank`.`3062_irnt_both_sexes` limit 10;
SELECT * FROM uk_biobank.variants WHERE chr=23 AND pos=2700027 AND variant="X:2700027:T:C" limit 1;

SELECT * FROM `uk_biobank`.`manifest` WHERE `manifest`.`Phenotype Code` = "3062_irnt" AND `manifest`.`Sex` = "both_sexes";

DESCRIBE `uk_biobank`.`3062_irnt_both_sexes`;
DESCRIBE `uk_biobank`.`3062_raw_both_sexes`;
DESCRIBE `uk_biobank`.`manifest`;
DESCRIBE `uk_biobank`.`variants`;

show index from `3062_irnt_both_sexes`;

ALTER TABLE `uk_biobank`.`3062_irnt_both_sexes` modify ref varchar(255);

ALTER TABLE `uk_biobank`.`3062_irnt_both_sexes` modify alt varchar(255);


ALTER TABLE `uk_biobank`.`3062_irnt_both_sexes` add primary key(chr, pos, ref, alt);

select * from `uk_biobank`.`variants` limit 10;


show index from `uk_biobank`.`3062_irnt_both_sexes`;
select * from `uk_biobank`.`variants` limit 10;
describe `uk_biobank`.`variants`;
select * from `uk_biobank`.`phenotypes_both_sexes` where phenotype='3064_irnt';


select `variants`.`chr`
    , `variants`.`pos`
	, `variants`.`ref`
	, `variants`.`alt`
	, `variants`.`rsid`
    , `variants`.`consequence`
    , `variants`.`consequence_category`
    , `variants`.`info`
    , `variants`.`call_rate`
    , `variants`.`AC`
    , `variants`.`minor_AF`
    , `variants`.`minor_allele`
    , `variants`.`n_hom_ref`
    , `variants`.`n_het`
    , `variants`.`n_hom_var`
    ,`3062_irnt_both_sexes`.`low_confidence_variant`
    ,`3062_irnt_both_sexes`.`ytx`
    ,`3062_irnt_both_sexes`.`beta`
    ,`3062_irnt_both_sexes`.`se`
    ,`3062_irnt_both_sexes`.`tstat`
    ,`3062_irnt_both_sexes`.`pval`
from `uk_biobank`.`variants`
inner join `uk_biobank`.`3062_irnt_both_sexes`
on `variants`.`variant` = `3062_irnt_both_sexes`.`variant`
where `variants`.`chr` = 1 and `variants`.`pos` >= 205000000 and `variants`.`pos` <= 207000000;

