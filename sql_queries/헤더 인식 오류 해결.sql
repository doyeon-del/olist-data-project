--- 테이블 헤더가 데이터로 적재된 오류를 수정하고 컬럼명을 재정의!

create or replace table `olist_raw.product_category_name_translation` as
select 
  string_field_0 as product_category_name,
  string_field_1 as product_category_name_english

from `olist_raw.product_category_name_translation`
where string_field_0 != 'product_category_name';