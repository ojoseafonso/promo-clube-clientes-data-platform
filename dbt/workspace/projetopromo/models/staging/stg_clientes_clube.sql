with source as (

    select *
    from {{ source('raw', 'CLIENTES_CLUBE') }}

),

renamed as (

    select
        cliente_id,
        cpf_hash,
        nome_completo,
        lower(email) as email,
        telefone,
        data_nascimento,
        sexo,
        cidade,
        estado,
        cep,
        canal_cadastro,
        data_cadastro,
        ultima_atualizacao,
        status_clube,
        opt_in_marketing,
        ticket_medio_estimado,
        origem_campanha
    from source

)

select *
from renamed
