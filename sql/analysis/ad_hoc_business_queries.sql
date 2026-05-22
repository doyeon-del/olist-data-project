
---- orders 테이블의 information 스키마 보기 
SELECT 
    column_name, 
    data_type 
FROM `olist_raw.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'orders';
--- 근데 사실 스키마 탭 활용해서 어떤 칼럼들이 있는지 봐주기만 하면 됨. 

--- <<<<< 본격적으로 쿼리문 짜보기 >>>>>>>
---- 미션 1. Olist 마켓플레이스에서, 가장 돈을 많이 벌어다 주는 카테고리는?
-- 뷰를 활용해 orders와 order_items, 그리고 product view 3중 조인하기 
select 
    vp.category_name_en,
    count(distinct o.order_id) as total_order_cnt,
    sum(oi.price) as total_revenue
from `olist_raw.orders` as o
join `olist_raw.order_items` as oi on o.order_id = oi.order_id
join `olist_raw.view_products_english` as vp on oi.product_id = vp.product_id
where o.order_status = 'delivered' 
group by vp.category_name_en
order by total_revenue desc ---- 수익에 따라 내림차순 정렬 
limit 10;

------ 미션 2. 신용카드(credit_card)로 결제된 건들의 총 결제 금액(payment_value)은 얼마인가?"

select round(sum(op.payment_value),2) as result
from `olist_raw.order_payments` as op 
where op.payment_type = 'credit_card';
