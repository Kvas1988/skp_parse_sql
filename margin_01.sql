select nyearfin,
       trunc(salesdate, 'MM') vmonth,
       ks as "ÊÑ",
       lfl13,
       lfl14,
       pl_nn,
       PLName,
       /*case
         when vclass like '7%' then
          upper(vclass)
         else
          vclass
       end vclass,*/
       vclass,
       sum(n1) as n,
       sum(s1) as S,
       sum(s_rur1) / 1000 as S_rur,
       sum(Inc1) as Inc,
       sum(Inc_r) / 1000 as Inc_r
  from (SELECT d.nyearfin,
               d.vmonth,
               salesdate,
               nvl(ks, 'Îïò') as ks,
               kust,
               report,
               lfl_yy as lfl13,
               lfl_y as lfl14,
               '' pl_nn,
               '' PLNAME,
               scb.vclass,
               
               -s.NVAL AS n1,
               (-s.RPRICEU) AS S1,
               (-s.RPRICE) AS S_rur1,
               
               -s.rpriceu +
               nvl2(ZPRICEU_Arrival, ZPRICEU_Arrival, nvl(s.zpriceu, 0)) -
               nvl2(nselfcostfusd,
                    (-s.nval) * (NSELFCOSTFUSD - NPRICEusd),
                    0) as Inc1,
                    
               -rprice - (case
                            when idtsupp = 2 and s.idtransact = 1 and not s.zprice is null then
                              -zprice
                            else
                              nvl2(NSELFCOSTF, (-s.nval) * (NSELFCOSTF), nvl(-s.zprice, 0))
                            end) * 
                            (case
                               when idtsupp = 2 and s.idtransact = 2 and nvl(supp.nvatpayer, 1) = 0 then
                                 case 
                                   when s.ddoclose > '31.12.2018' then
                                     1.2
                                   else
                                     1.18
                                 end
                               else
                                 1
                             end) as Inc_r
        
          FROM MAKER.RAW$SALES            s,
               MAKER.Olap$FIRM2           f,
               MAKER.RAW$LOGPLACE         rlp,
               maker.olap$logplace2       OLP,
               maker.raw$fullart          fa,
               CENTER.DOLIST_SELFCOST     sc,
               maker.dim$goods            g,
               maker.raw$classes_link_all c,
               maker.dim_date             d,
               /*maker.rpas$subclass3       scb,*/
               vklim.subclass4            scb,
               maker.rpas$subclass_mart   scm,
               MAKER.DIM$SUBSEASON        dss,
               vklim.cm_idmfc             c2,
               maker.raw$supp             supp
        
   WHERE (s.salesdate between
         (case
            when extract(month from sysdate-1) in (1,2) then
              to_date('01.02.'||(extract (year from sysdate-1)-3)) 
            else
              to_date('01.02.'||(extract (year from sysdate-1)-2)) 
          end)  AND trunc(add_months(sysdate-1,-24), 'mm') - 1  
          
          OR
          
         s.salesdate between
         (case
            when extract(month from sysdate-1) in (1,2) then
              to_date('01.03.'||(extract (year from sysdate-1)-2)) 
            else
              to_date('01.03.'||(extract (year from sysdate-1)-1)) 
          end)  AND trunc(add_months(sysdate-1,-12), 'mm') - 1

          OR
          
         s.salesdate between
         (case
            when extract(month from sysdate-1) in (1,2) then
              to_date('01.03.'||(extract (year from sysdate-1)-1)) 
            else
              to_date('01.03.'||(extract (year from sysdate-1))) 
          end)  AND trunc(sysdate, 'mm')-1         
          )            
                          
              
           and rlp.idmartcard(+) = s.idmartcard
           and OLP.plcode(+) = rlp.plcode
           and f.idfirm(+) = s.idfirm
           and d.day_id(+) = s.salesdate
           and sc.iddolist(+) = s.iddolist
           and fa.idmartcard(+) = S.idmartcard
           and scb.idsubclass(+) = nvl(scm.idsubclass, 81)
           and scm.idmartcard(+) = s.idmartcard
           and g.iddolist(+) = s.iddolist
           and c.idmartcard(+) = s.idmartcard
           and dss.iddolist(+) = s.iddolist
           and c2.idmfc(+) = fa.idmfc
           and supp.idsupp(+) = s.idsupp
           and not nvl(rlp.plcode, 0) in (19,21)
           and scb.idclass not in (1000)
        
        )
 group by nyearfin,
          trunc(salesdate, 'MM'),
          ks,
          pl_nn,
          lfl13,
          lfl14,
          /*case
            when vclass like '7%' then
             upper(vclass)
            else
             vclass
          end*/
          vclass
          
 order by nyearfin
