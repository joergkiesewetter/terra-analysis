import os
from datetime import datetime

import config
from provider.terra import Terra
from util import logging

BASE_DIRECTORY = '/terra/raw/transactions'

log = logging.get_custom_logger(__name__, config.LOG_LEVEL)


token = dict()

def update_token_transactions():
    """

    fetches all transactions.

    :return:
        Nothing
    """

    os.makedirs(BASE_DIRECTORY, exist_ok=True)


    # symbol_dir = BASE_DIRECTORY + symbol
    #
    # os.makedirs(symbol_dir, exist_ok=True)

    max_time = datetime.utcnow()
    max_time = max_time.replace(hour=0, minute=0, second=0, microsecond=0)

    last_timestamp, last_block, last_hash = _get_last_transaction()

    log.debug('starting update from block: ' + str(last_block))
    if last_hash:
        log.debug('with hash: ' + last_hash)
    log.debug('with timestamp: ' + str(last_timestamp))

    transactions = Terra.get_transaction(last_block)

    _clear_last_block(last_block)

    max_time_exceeded = False

    while not max_time_exceeded:

        log.debug('storing block ' + str(last_block))


        for transaction in transactions:

            # last_batch_block = last_block
            # last_batch_timestamp = last_timestamp
            # last_batch_hash = last_hash

            block_number = transaction['block']
            timestamp = datetime.utcfromtimestamp(int(transaction['timestamp']))
            hash = transaction['txhash']
            type = transaction['type']

            if timestamp > max_time:
                max_time_exceeded = True
                break

            if type not in token.keys():
                token[type] = {
                    'directory': os.path.join(BASE_DIRECTORY, type.replace('/', '_')),
                    'file': None,
                    'filename': None
                }

                os.makedirs(token[type]['directory'], exist_ok=True)

            act_filename = timestamp.strftime('%Y-%m-%d') + '.csv'
            if not token[type]['file'] or act_filename != token[type]['filename']:
                token[type]['filename'] = act_filename

                if token[type]['file']:
                    token[type]['file'].close()

                token[type]['file'] = open(os.path.join(token[type]['directory'], token[type]['filename']), 'a')

            if type == 'distribution/MsgWithdrawDelegationReward':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['delegator'],
                                     transaction['validator'],
                                    ])

            elif type == 'distribution/MsgWithdrawValidatorCommission':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['validator'],
                                    ])

            elif type == 'gov/MsgSubmitProposal':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['proposer'],
                                     transaction['init_deposit_amount'],
                                     transaction['init_deposit_currency'],
                                     transaction['proposal_id'],
                                     transaction['proposal_title'],
                                     transaction['proposal_text'],
                                    ])

            elif type == 'gov/MsgDeposit':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['depositor'],
                                     transaction['proposal_id'],
                                     transaction['amount'],
                                     transaction['currency'],
                                    ])

            elif type == 'staking/MsgDelegate':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['delegator'],
                                     transaction['validator'],
                                     transaction['amount'],
                                     transaction['currency'],
                                    ])

            elif type == 'market/MsgSwap':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['ask_address'],
                                     transaction['ask_amount'],
                                     transaction['ask_currency'],
                                     transaction['bid_address'],
                                     transaction['bid_amount'],
                                     transaction['bid_currency'],
                                    ])

            elif type == 'staking/MsgEditValidator':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['address'],
                                     transaction['details'],
                                     transaction['moniker'],
                                     transaction['website'],
                                     transaction['identity'],
                                     transaction['commission_rate'],
                                     transaction.get('min_self_delegation') or '',
                                    ])

            elif type == 'staking/MsgCreateValidator':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['pubkey'],
                                     transaction['amount'],
                                     transaction['currency'],
                                     transaction['commission_rate'],
                                     transaction['commission_max_rate'],
                                     transaction['commission_max_change_rate'],
                                     transaction['details'],
                                     transaction['moniker'],
                                     transaction['website'],
                                     transaction['identity'],
                                     transaction['min_self_delegation'],
                                     transaction['delegator'],
                                     transaction['validator'],
                                    ])

            elif type == 'oracle/MsgExchangeRateVote':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     str(transaction['exchange_rate']),
                                     transaction['currency'],
                                    ])

            elif type == 'oracle/MsgExchangeRatePrevote':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     transaction['currency'],
                                    ])

            elif type == 'oracle/MsgDelegateFeedConsent':
                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                    ])

            elif type == 'bank/MsgMultiSend':

                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     str(transaction['amount']),
                                     transaction['currency'],
                                     transaction['from_address'],
                                     transaction['to_address'],
                                     str(transaction['tax_amount']),
                                     transaction['tax_currency'],
                                    ])

            elif type == 'bank/MsgSend':

                new_line = ','.join([str(transaction['block']),
                                     str(transaction['timestamp']),
                                     transaction['txhash'],
                                     str(transaction['amount']),
                                     transaction['currency'],
                                     transaction['from_address'],
                                     transaction['to_address'],
                                     str(transaction['tax_amount']),
                                     transaction['tax_currency'],
                                    ])
            else:
                new_line = ''
                log.warning('transaction type not known: ' + type)

            token[type]['file'].write(new_line + '\n')

            last_timestamp = timestamp
            # last_block = block_number
            last_hash = hash

        # log.debug('last block: ' + str(last_batch_block))
        # log.debug('last timestamp: ' + str(last_batch_timestamp))
        last_block += 1
        transactions = Terra.get_transaction(last_block)

        # if last_timestamp == last_batch_timestamp and last_block == last_batch_block and last_hash == last_batch_hash:
        #     break

        # last_timestamp = last_batch_timestamp
        # last_block = last_batch_block
        # last_hash = last_batch_hash

        for key in token.keys():
            if token[key]['file']:
                token[key]['file'].flush()
                os.fsync(token[key]['file'].fileno())
                token[key]['file'].close()
                token[key]['file'] = None


def _clear_last_block(block_number):

    directories = [f for f in os.listdir(BASE_DIRECTORY) if os.path.isdir(os.path.join(BASE_DIRECTORY, f))]

    for directory in directories:

        path = os.path.join(BASE_DIRECTORY, directory)
        last_file_timestamp = None
        last_file = None

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # get the file with the highest timestamp
        for file in files:
            filename = file.split('.')[0]

            timestamp = datetime.strptime(filename, '%Y-%m-%d')

            if not last_file_timestamp or timestamp > last_file_timestamp:
                last_file_timestamp = timestamp
                last_file = file

        if not last_file:
            return

        log.debug('removing data from the last block')
        log.debug('scanning for block number: ' + str(block_number) + ' in directory \'' + directory + '\'')
        removed_lines = 0

        new_lines = []
        with open(os.path.join(path, last_file), 'rt') as file:

            for line in file:

                line_split = line.split(',')

                if str(line_split[0]) != str(block_number):
                    new_lines.append(line)
                else:
                    removed_lines += 1

            file.flush()
            file.close()

        log.debug('removing number of lines: ' + str(removed_lines))

        with open(os.path.join(path, last_file), 'w') as file:
            for line in new_lines:
                file.write(line)
            file.flush()
            file.close()


def _get_last_transaction():

    last_timestamp = 0
    # TODO change back to 0
    last_block = 0
    last_hash = None

    directories = [f for f in os.listdir(BASE_DIRECTORY) if os.path.isdir(os.path.join(BASE_DIRECTORY, f))]

    for directory in directories:

        path = os.path.join(BASE_DIRECTORY, directory)
        last_file_timestamp = None
        last_file = None

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

        # get the file with the highest timestamp
        for file in files:
            filename = file.split('.')[0]

            timestamp = datetime.strptime(filename, '%Y-%m-%d')

            if not last_file_timestamp or timestamp > last_file_timestamp:
                last_file_timestamp = timestamp
                last_file = file

        # if we don't have stored data for the given symbol
        if not last_file:
            return 0, 0, None

        # if the file exists, but is empty
        if os.stat(os.path.join(path, last_file)).st_size <= 0:
            continue

        # getting the last line of the file an extract the timestamp
        with open(os.path.join(path, last_file), 'rt') as file:

            last_line = file.readlines()[-1]

            last_line = last_line.split(',')

            if last_block is None or last_timestamp < int(last_line[1]):
                last_timestamp = int(last_line[1])
                last_block = int(last_line[0])
                last_hash = last_line[2]


    return last_timestamp, last_block, last_hash


def get_first_transaction_timestamp(symbol):

    last_file_timestamp = None

    dir = os.path.join(BASE_DIRECTORY, symbol)

    files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

    # get the file with the highest timestamp
    for file in files:
        filename = file.split('.')[0]

        timestamp = datetime.strptime(filename, '%Y-%m-%d')

        if not last_file_timestamp or timestamp < last_file_timestamp:
            last_file_timestamp = timestamp

    return last_file_timestamp


def get_transaction_data(symbol, date):

    try:
        with open(os.path.join(BASE_DIRECTORY, symbol, date.strftime('%Y-%m-%d') + '.csv'), 'rt') as file:

            return_data = []


            for line in file:
                return_data.append(line.split(','))

            return return_data
    except:
        return []