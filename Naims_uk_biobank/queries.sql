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