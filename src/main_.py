# -*- coding: utf-8 -*-
"""
Created on Fri Jan 25 20:12:07 2019

@author: Ljx
"""


import models, data
from utils.visualize import Visualizer 
from config import opt
import torch as t, numpy as np
import warnings
from torch.utils.data import DataLoader

from models.VAR import VAR

def train(f='train'):
    if f=='train':
        opt.tr_va_te = 0
    # model
    model = getattr(models, opt.model)(opt = opt)
    if opt.load_model_path:
        model.load(opt.load_model_path)
    model.to(opt.device)
    model.train()
    # data
    train_data = data.datasets(opt).getData()
    train_dataloader = DataLoader(train_data, opt.batch_size, shuffle = True)
    # certerion & optimzer
    certerion = t.nn.MSELoss()
    optimizer = t.optim.Adam(model.parameters(),
                             lr = opt.lr, 
                             weight_decay = opt.weight_decay)
    # losses
    iter_losses = [] # np.zeros(opt.batch_size * opt.max_epoch)
    epoch_losses = [] # np.zeros(opt.max_epoch)
    
    #train
    for epoch in range(opt.max_epoch):
#        print('model : ',opt.model,', epoch : ',epoch)
        temp_loss = []
        for _, (d_t, ts) in enumerate(train_dataloader):
#            print(_, end=' ')
            input_data = d_t[0].to(opt.device)
            target_data = d_t[1].to(opt.device)
            
            optimizer.zero_grad()
            input_data = input_data.permute(1,0,2)
            target_data = target_data.permute(1,0,2)
#            print(input_data.size(), target_data.size())
#            if input_data.shape[1] < opt.batch_size:
#                continue
            if 'VAR' in opt.model:
                output_data = model([input_data, target_data])
            else:
                output_data = model(input_data)
            # i: T * batch * multi; t: future * batch * output_size; o: future * batch * output_size
#            print(input_data.size(), target_data.size(), output_data.size())
            loss = certerion(target_data, output_data)
            loss.backward()
            optimizer.step()
            iter_losses.append(loss.item())
            temp_loss.append(loss.item())
# =============================================================================
#             if loss.item() < .0001 or _ == 0:
#                 i_ = input_data.detach().cpu().numpy()
#                 o_ = output_data.detach().cpu().numpy()
#                 t_ = target_data.detach().cpu().numpy()
#                 Visualizer().drawTest((i_, o_, t_), ts)
# =============================================================================
#            break
#        break
            
        epoch_losses.append(np.mean(temp_loss))
        if epoch % 5 == 3:
            print('model:',opt.model,' ,epoch:',epoch,' ,loss:',epoch_losses[-1], opt.lr)
        if epoch > 3 and epoch_losses[-1] > epoch_losses[-2]:
            opt.lr = opt.lr * opt.lr_decay
#        if epoch % 10 == 5:
#            opt.lr = opt.lr * opt.lr_decay
    path = model.save(opt)
    return epoch_losses, iter_losses, path

def val():
    opt.max_epoch = 5
    opt.tr_va_te = 1
    return train(f='val')
    
def test():
    opt.tr_va_te = 2
    return modelTestSimple(), None, None
    
def modelTestSimple():
    opt.batch_size = 1
    
    model = getattr(models, opt.model)(opt = opt).eval()
    if opt.load_model_path:
        model.load(opt.load_model_path)
    model.to(opt.device)
    test_data =  data.datasets(opt).getData()
    
    loss = []
    for _ in range(opt.num):
        index = np.random.randint(0, len(test_data) - 1)
        def datatype(test_data, index):
            d_t, ts = test_data[index]
            i = d_t[0].to(opt.device).unsqueeze(0).permute(1,0,2)
            t = d_t[1].to(opt.device).unsqueeze(0).permute(1,0,2)
            ts = (ts[0].to(opt.device).unsqueeze(0), ts[1].to(opt.device).unsqueeze(0))
            return i, t, ts
        input_data, target_data, ts = datatype(test_data, index)
        if 'VAR' in opt.model:
            output_data = model([input_data, target_data])
        else:
            output_data = model(input_data)
        # i: T * batch(1) * multi; t: future * batch(1) * multi; o: future * batch(1) * multi
        temp_loss = t.nn.MSELoss()(target_data, output_data).item()
        print('temp_loss : ', temp_loss)
        def tensor2numpy(i_, o_, t_):
            return i_.cpu().detach().numpy(), \
                o_.cpu().detach().numpy(), \
                t_.cpu().detach().numpy()
        Visualizer().drawTest(tensor2numpy(input_data, output_data, target_data), ts)
        print(temp_loss)
        loss.append(temp_loss)
    return loss

def pre(f='pre'):
    opt.tr_va_te = 2
    
    model = getattr(models, opt.model)(opt = opt).eval()
    if opt.load_model_path:
        model.load(opt.load_model_path)
    model.to(opt.device)
#    print('\n\n', list(model.out_sigma.named_parameters()), '\n\n')
    return pre_(model)
    
def pre_(model):
    test_data = data.datasets(opt).getData()
    N = test_data.__len__()
    if opt.num > N :
        warnings.warn('Warning: data is not long enough, data(%d) num(%d)' % (N, opt.num))
    start_index = 0
    all_input_data = None
    all_output_data = None
    all_target_data = None
    all_ts = None
    loss = []
    index = start_index
    while index - start_index < opt.num:
        def datatype(test_data, index):
            d_t, ts = test_data[index]
            i = d_t[0].to(opt.device).unsqueeze(0).permute(1,0,2)
            t = d_t[1].to(opt.device).unsqueeze(0).permute(1,0,2)
            return i, t, ts
        input_data, target_data, ts = datatype(test_data, index)
        if 'VAR' in opt.model:
            output_data = model([input_data, target_data])
        else:
            output_data = model(input_data)
#        print(target_data.shape,output_data.shape)
        temp_loss = t.nn.MSELoss()(target_data, output_data).item()
        loss.append(temp_loss)
        def tensor2numpy(i_, o_, t_):
            return i_.cpu().detach().numpy(), \
                o_.cpu().detach().numpy(), \
                t_.cpu().detach().numpy()
        i_, o_, t_ = tensor2numpy(input_data, output_data, target_data)
        all_input_data = i_ if all_input_data is None else np.concatenate([all_input_data, i_])
        all_output_data = o_ if all_output_data is None else np.concatenate([all_output_data, o_])
        all_target_data = t_ if all_target_data is None else np.concatenate([all_target_data, t_])
        all_ts = ts if all_ts is None else (t.cat((all_ts[0], ts[0]), dim = 0), t.cat((all_ts[1], ts[1]), dim = 0))
        index += opt.future
    print(all_input_data.shape, all_output_data.shape, all_target_data.shape)
    all_ts = (all_ts[0].unsqueeze(0), all_ts[1].unsqueeze(0))
    Visualizer().drawTest(([], all_output_data, all_target_data), all_ts, drawLot = True)
    evaluation(t.from_numpy(all_output_data), t.from_numpy(all_target_data), 0)
    return loss, None, None
    
def evaluation(output, target, batch):
    print('model: ',opt.model)
    for i in range(8):
        print(i)
        numerator = t.sqrt(t.mean(t.pow(output[:,batch,i:i+1]-target[:,batch,i:i+1],2)))
        denominator_u = t.sqrt(t.mean(t.pow(target[:,batch,i:i+1],2))) * t.sqrt(t.mean(t.pow(output[:,batch,i:i+1],2)))
        MSE = t.mean(t.pow(output[:,batch,i:i+1]-target[:,batch,i:i+1],2)).item()
        U = t.div(numerator, denominator_u).item()
        print('MSE: ',MSE)
        print('U: ',U)
    
def traditional():
    opt.batch_size = 1
    opt.tr_va_te = 2
    pre_(VAR(opt).predict)
    

def help():
    pass

def LetsGo(kwargs, fun):
    if kwargs is not None:
        opt._parse(kwargs)
    opt.input_size = opt._input_kv[opt.data]
    opt.output_size = opt._output_kv[opt.data]
    opt.needLog = opt._needLog_kv[opt.data]
    if opt.model == 'VAR':
        traditional()
        return
    epoch_losses, iter_losses, path = fun()
    print('path : ',path)
    print('loss : \n' , np.mean(epoch_losses))
    if len(epoch_losses) > 1:
        Visualizer().drawEpochLoss(epoch_losses[3:])
    print('min: ', min(epoch_losses))
    print('\n','epoch_losses:\n',epoch_losses)
    

if __name__ == '__main__':
    t.set_default_tensor_type('torch.DoubleTensor')

    m_path = 'checkpoints/TCN_NINO_0125210803.pth' 
    m_path = None
    
    '''
    LSTM, LSTM_ATT, LSTM_VAR, LSTM_ATT_VAR, VAR, 
    R2N2_VAR, LSTNet_skip, LSTNet_Attn, TCN, 
    LSTM_VAR_PID, LSTM_ATT_VAR_PID, LSTM_VAR_PID_Sigma, LSTM_ATT_VAR_PID_Sigma, 
    CNN_LSTM, Wavelet_ATT
    '''
    m_model = 'TCN' 
    m_data = 'NINO' # NINO, Yahoo, Wecar, Aircraft, BJpm   ExchangeRate GEFCom2014_Task1_P
    m_lr = 0.001
    m_num = 80
    
    
    mm = {'load_model_path':m_path, 'model':m_model, 'data':m_data, 
          'lr':m_lr, 'num':m_num}
    
    LetsGo(mm, pre) # train, val, test, pre
    
    opt._parse(printconfig = True)
    
    
