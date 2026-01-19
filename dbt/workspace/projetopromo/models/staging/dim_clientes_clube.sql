with clientes as (

    select *
    from {{ ref('stg_clientes_clube') }}

),

validacoes as (

    select
        cliente_id,
        cpf_hash,
        nome_completo,
        email,
        canal_cadastro,
        data_cadastro,

        case
            when status_clube = 'ATIVO'
             and opt_in_marketing = true
             and data_cadastro <= dateadd(minute, -5, current_timestamp)
            then true
            else false
        end as cliente_elegivel_promocao

    from clientes

)

select *
from validacoes
