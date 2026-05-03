--- product에 있는 category 열을 영어로 번역. category_name_en 열로 만들기 
select 
  p.product_id, 
  coalesce(t.product_category_name_english, p.product_category_name, 'unknown') as category_name_en,
  p.product_weight_g,
  p.product_length_cm,
  p.product_height_cm,
  p.product_width_cm,

from `olist_raw.products` p

left join `olist_raw.product_category_name_translation` t
on p.product_category_name = t.product_category_name;

--- 번역되지 않은 카테고리 확인용 쿼리 : 
select distinct p.product_category_name
from  `olist_raw.products` p
left join `olist_raw.product_category_name_translation` t
on p.product_category_name = t.product_category_name
where t.product_category_name_english is null;

--- 결과: 총 3개였음. null, pc_gamer, portateis_cozinha_e_preparadores_de_alimentos


---- 최종 JOIN 쿼리 -------
---- 원래 null인 행이라면 Unknown으로, pc_gamer라면 pc_gamer 값 자체로, 하나의 포르투갈어라면 번역한 값이 들어갈 수 있도록!
select 
  p.product_id,
  case ---- 위에서 확인한 번역 안 된 값들 확인 
    when p.product_category_name is null then 'unknown'
    when p.product_category_name = 'pc_gamer' THEN 'pc_gamer'
    when p.product_category_name = 'portateis_cozinha_e_preparadores_de_alimentos' THEN 'portable_kitchen_food_preparers'
    else coalesce(t.product_category_name_english, p.product_category_name)
  end as category_name_en,
  p.product_weight_g,
  p.product_length_cm,
  p.product_height_cm,
  p.product_width_cm

from `olist_raw.products` p

left join `olist_raw.product_category_name_translation` t
on p.product_category_name = t.product_category_name;

----- 위 join 쿼리를 쓸 필요가 없도록, 위 결과물을 view로 고정해두기!

create or replace view `olist_raw.view_products_english` as
select 
  p.product_id,
  case ---- 위에서 확인한 번역 안 된 값들 확인 
    when p.product_category_name is null then 'unknown'
    when p.product_category_name = 'pc_gamer' THEN 'pc_gamer'
    when p.product_category_name = 'portateis_cozinha_e_preparadores_de_alimentos' THEN 'portable_kitchen_food_preparers'
    else coalesce(t.product_category_name_english, p.product_category_name)
  end as category_name_en,
  p.product_weight_g,
  p.product_length_cm,
  p.product_height_cm,
  p.product_width_cm

from `olist_raw.products` p

left join `olist_raw.product_category_name_translation` t
on p.product_category_name = t.product_category_name;


